import socket
import logging
import threading
import time
import subprocess

from signal import signal, SIGTERM


"""
OPCODES:
0x05 - STATREQ: Solicitar estado de un servicio.
0x0A - SERVICE_NAME: Respuesta de un servicio a STATREQ. los siguientes bytes corresponden al nombre del servicio.
0x0B - PEER_ID: Respuesta de un peer a STATREQ. Los siguientes bytes corresponden al ID del peer.
0x0C - VOTE_SERVICE: Solicitud de voto a un peer. Los siguientes bytes corresponden al servicio que se debe votar.
0x0F - VOTE_RESPONSE: Respuesta de voto de un peer. El byte siguiente corresponde a un booleano 0 si el servicio esta funcionando correctamente o 1 si no.
"""
class HealthChecker:
    def __init__(self, identifier: int, services_names: list, retries=3, timeout=2):
        self.id = identifier
        self.leader_id = self.id
        self.health_service_name = 'health_checker_'
        self.listen_port = 8080
        self.retries = retries
        self.timeout = timeout
        self.stop = False

        try:
            services_names.remove(f'{self.health_service_name}{self.id}')
        except ValueError:
            pass
        self.services = services_names

        self.peers = {}
        self.failed_services = []
        self.failed_services_votes = {}

        # Socket UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.listen_port))
        self.sock.settimeout(self.timeout)

        self.lock = threading.Lock()

        signal(SIGTERM, self.signal_exit)

    def signal_exit(self, signum, frame):
        self.stop = True

        self.sock.close()

    def write(self, msg: bytes, service: str):
        bytes_sent = 0
        while bytes_sent < len(msg):
            bytes_sent += self.sock.sendto(msg, (service, self.listen_port))

    def read(self) -> tuple[bytes, tuple[str, int]]:
        return self.sock.recvfrom(4096)

    def send_statreq(self, services):
        """Envía mensajes STATREQ a los servicios especificados."""
        for service in services:
            try:
                self.write(0x05.to_bytes(1, 'big'), service)
            except socket.error as e:
                logging.error(f"action: send_status_request | result: error | info: error al enviar solicitud de estado al servicio {service}: {e}")

    def handle_response(self, data, addr):
        """Procesa una respuesta recibida."""

        if len(data) < 1:
            return

        service_type = data[0]

        with self.lock:
            if service_type == 0x05:
                msg = bytes([0x0B, self.id])
                self.write(msg, addr[0])

            elif service_type == 0x0A:
                service_name = data[1:].decode('utf-8')
                try:
                    self.failed_services.remove(service_name)
                    logging.info(f"action: health_check | result: success | info: el servicio {service_name} respondió correctamente")
                except ValueError:
                    pass

            elif service_type == 0x0B:
                peer_id = data[1]
                try:
                    self.failed_services.remove(f'{self.health_service_name}{peer_id}')
                    logging.info(f"action: health_check | result: success | info: el servicio {self.health_service_name}{peer_id} respondió correctamente")
                except ValueError:
                    pass
                if peer_id not in self.peers:
                    self.peers[peer_id] = addr
                    if peer_id > self.leader_id:
                        self.leader_id = peer_id
                        logging.info(f"action: health_check | result: success | info: el peer con ID {peer_id} es el nuevo lider")
                    logging.info(f"action: health_check | result: success | info: nuevo peer encontrado en {addr[0]} con ID {peer_id}")

            elif service_type == 0x0C:
                service = data[1:].decode('utf-8')
                if service not in self.failed_services:
                    msg = bytes([0x0F, self.id, 0]) + service.encode(encoding="utf-8")
                else:
                    msg = bytes([0x0F, self.id, 1]) + service.encode(encoding="utf-8")
                self.write(msg, addr[0])
                logging.info(f"action: health_check | result: success | info: respondida solicitud de voto para el servicio {addr}")

            elif service_type == 0x0F:
                peer_id = data[1]
                vote = data[2]
                service = data[3:].decode('utf-8')
                self.failed_services_votes[service] = self.failed_services_votes.get(service, 0)
                if vote:
                    self.failed_services_votes[service] += 1
                else:
                    self.failed_services_votes[service] -= 1
                logging.info(f"action: health_vote | result: success | info: peer con ID {peer_id} votó que {'está caido' if vote else 'no está caido'} el servicio {service}")

    def listen_for_responses(self):
        """Escucha respuestas y las maneja en threads separados."""
        while not self.stop:
            try:
                data, addr = self.read()
                threading.Thread(target=self.handle_response, args=(data, addr)).start()
            except socket.timeout:
                break
            except Exception as e:
                logging.error(f"action: receive_responses | result: fail | info: {e}")

    def scan_services(self):
        """Escanea los puertos con reintentos."""
        self.peers = {}
        self.leader_id = self.id
        self.failed_services_votes.clear()
        self.failed_services = self.services.copy()

        for attempt in range(self.retries):
            if not self.failed_services:
                logging.debug("action: scan_services | result: success | info: todos los servicios respondieron correctamente")
                return
            logging.debug(f"action: scan_services | result: in_progress | info: intento {attempt + 1} de {self.retries}")

            services_to_scan = self.failed_services.copy()

            self.send_statreq(services_to_scan)

            time.sleep(self.timeout)

        if self.failed_services:
            logging.debug(f"action: scan_services | result: success | info: servicios fallidos: {', '.join(self.failed_services)}")
            if self.leader_id == self.id:
                logging.debug("action: consensuate_service_down | result: in_progress | info: iniciando proceso de consenso para servicios fallidos")
                self.broadcast_consensus()
        else:
            logging.debug("action: scan_services | result: success | info: todos los servicios respondieron correctamente")

    def broadcast_consensus(self):
        """Implementa un algoritmo de consenso basado en broadcast y votación."""
        if not self.peers:
            logging.warning("action: consensuate_service_down | result: in_progress | info: no se encontraron peers, reviviendo servicios fallidos...")
            for service in self.failed_services:
                self.revive_service(service)
            return

        for service in self.failed_services:
            logging.info(f"action: consensuate_service_down | result: in_progress | info: consensuando servicio {service}...")

            request_msg = bytes([0x0C]) + service.encode(encoding='utf-8')
            for peer_id, peer_addr in self.peers.items():
                self.write(request_msg, peer_addr[0])
                logging.debug(f"action: vote_request_sent | result: success | peer: {peer_id} | service: {service}")

            time.sleep(self.timeout)

            if self.failed_services_votes.get(service, -1) >= 0:
                logging.info(f"action: consensuate_service_down | result: success | info: la mayoría votó que el servicio {service} está caído, reviviendo...")
                self.revive_service(service)
            else:
                logging.info(f"action: consensuate_service_down | result: success | info: la mayoría votó que el servicio {service} no está caído.")

    def revive_service(self, service_name):
        if service_name not in self.services:
            logging.warning(f"action: revive_service | result: success | info: no se puede revivir servicio {service_name}")
            return
        result = subprocess.run(["docker", "start", service_name])
        logging.info(f"action: revive_service | result: success | info: codigo de retorno: {result.returncode} | salida: {result.stdout} | codigo de error: {result.stderr}")

    def start(self):
        while not self.stop:
            time.sleep(5)

            scan_thread = threading.Thread(target=self.scan_services)
            listen_thread = threading.Thread(target=self.listen_for_responses)

            listen_thread.start()
            scan_thread.start()

            scan_thread.join()
