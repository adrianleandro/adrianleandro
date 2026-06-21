import socket
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import nltk
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from signal import signal, SIGTERM

class Server:
    def __init__(self, port, listen_backlog, max_workers=10):
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.exit_program = False
        self.model = NaiveBayesAnalyzer()

    def signal_exit(self, signum, frame):
        self.exit_program = True

        self._thread_pool.shutdown(wait=False)

        self._server_socket.close()

    def run(self):
        """
        Server main loop

        Server that accepts new connections and establishes
        communication with clients. After client communication
        finishes, server starts to accept new connections again.
        Handles errors gracefully to prevent server crashes.
        """
        signal(SIGTERM, self.signal_exit)

        while not self.exit_program:
            try:
                client_sock = self.__accept_new_connection()
                self._thread_pool.submit(self.__handle_client_connection, client_sock)
            except OSError as e:
                if self.exit_program:
                    logging.info(f'action: close | result: success')
                else:
                    logging.error(f'action: accept_connection | result: error | error: {e}')


    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:

            chunks = []
            total_size = 0
            max_size = 1024 * 1024

            while True:
                chunk = client_sock.recv(max_size)
                if not chunk:
                    break

                chunks.append(chunk)
                total_size += len(chunk)

                if total_size > max_size:
                    logging.warning(f"action: receive_message | result: fail | error: Message too large")
                    return

                if b'\n' in chunk:
                    break

            msg = b''.join(chunks).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')

            sentiment = self.analyze_sentiment(msg)
            logging.info(f'action: analyze_sentiment | result: success | msg: {msg} | sentiment: {sentiment}')

            if sentiment == 'pos':
                data_to_send = bytes('1', encoding='utf-8')
            else:
                data_to_send = bytes('0', encoding='utf-8')

            bytes_sent = 0
            while bytes_sent < len(data_to_send):
                sent = client_sock.send(data_to_send[bytes_sent:])
                if sent == 0:
                    raise OSError('Socket closed')
                bytes_sent += sent

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made or timeout occurs.
        Then connection created is logged and returned.
        Handles potential errors during connection acceptance.
        """
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            logging.error(f'action: accept_connections | result: error | error: {e}')
            raise

    def analyze_sentiment(self, text):
        sentiment = TextBlob(text, analyzer=self.model).sentiment
        return sentiment.classification
