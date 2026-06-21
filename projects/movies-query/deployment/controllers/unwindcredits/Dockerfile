FROM golang:1.24.2-alpine3.21 AS BUILDER
RUN mkdir -p /build
WORKDIR /build/

COPY go.mod go.sum ./
RUN go mod download

COPY cmd cmd 
COPY configs configs
COPY internal internal
COPY utils utils
RUN go build -o bin/main ./cmd/controllers/unwindcredits/main.go

FROM golang:1.24.2-alpine3.21 AS RUNNER
WORKDIR /app
COPY --from=BUILDER /build/bin/main ./main
CMD ["./main"]