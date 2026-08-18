package main

import (
	"bytes"
	"encoding/binary"
	"io"
	"log"
	"net"
	"net/http"
	"strings"
	"time"
)

// Global Configuration Settings for our Startup Middleware
const (
	ListenAddress = "0.0.0.0:5433"   // The port other apps/DBeaver connect to
	TargetDB      = "localhost:5432" // The actual active Docker storage database
	AIEngineURL   = "http://localhost:8000/optimize" // Python AI Brain server link
	HardTimeout   = 3 * time.Millisecond // Layer 2: Strict 3ms hardware limit
)

func main() {
	listener, err := net.Listen("tcp", ListenAddress)
	if err != nil {
		log.Fatalf("🛑 Critical Production Failure: Could not bind gateway on %s: %v", ListenAddress, err)
	}
	defer listener.Close()

	log.Printf("🚀 AutoSQL AI Engine: Production wire-protocol proxy active on %s", ListenAddress)

	for {
		clientConn, err := listener.Accept()
		if err != nil {
			log.Printf("⚠️ Connection Error: Failed to accept incoming socket: %v", err)
			continue
		}
		// Launch an isolated routine for each customer app instance
		go handleClientSession(clientConn)
	}
}

func handleClientSession(clientConn net.Conn) {
	defer clientConn.Close()

	// Connect directly down into the Docker production database
	dbConn, err := net.Dial("tcp", TargetDB)
	if err != nil {
		log.Printf("🛑 Database Routing Blocked: Container offline on port 5432: %v", err)
		return
	}
	defer dbConn.Close()

	// --- LAYER 1: POSTGRESQL WIRE PROTOCOL HANDSHAKE INTEGRATION ---
	// Read the initial startup payload block sent by DBeaver / Client Apps
	headerBuf := make([]byte, 8)
	if _, err := io.ReadFull(clientConn, headerBuf); err != nil {
		return
	}

	packetLength := binary.BigEndian.Uint32(headerBuf[0:4])
	protocolCode := binary.BigEndian.Uint32(headerBuf[4:8])

	// Check if the client application is attempting an SSL handshake negotiation request
	if protocolCode == 80877103 { 
		// Send back 'N' to tell DBeaver to safely process via standard unencrypted protocol channel
		clientConn.Write([]byte{'N'})
		// Re-read the actual subsequent database schema connection packet
		if _, err := io.ReadFull(clientConn, headerBuf); err != nil {
			return
		}
		packetLength = binary.BigEndian.Uint32(headerBuf[0:4])
	}

	// Read remaining configuration body metrics from the wire packet stream
	payloadSize := packetLength - 8
	payloadBuf := make([]byte, payloadSize)
	if _, err := io.ReadFull(clientConn, payloadBuf); err != nil {
		return
	}

	// Forward complete sanitized initialization metrics down directly to Docker
	var completeHandshake bytes.Buffer
	completeHandshake.Write(headerBuf)
	completeHandshake.Write(payloadBuf)
	if _, err := dbConn.Write(completeHandshake.Bytes()); err != nil {
		return
	}

	// Establish bidirectional pipeline between client socket context and Docker database storage
	go io.Copy(clientConn, dbConn)

	// Stream reader loop to intercept client database execution packets
	queryPacket := make([]byte, 4096)
	for {
		n, err := clientConn.Read(queryPacket)
		if err != nil {
			return // Session completed normally or socket pipe dropped
		}

		rawPacketData := queryPacket[:n]
		
		// Look for standard PostgreSQL 'Simple Query' identifier character byte ('Q')
		if len(rawPacketData) > 5 && rawPacketData[0] == 'Q' {
			extractedSQL := string(rawPacketData[5 : len(rawPacketData)-1])
			trimmedSQL := strings.TrimSpace(extractedSQL)

			log.Printf("📥 Intercepted SQL Traffic Stream: %s", trimmedSQL)

			// --- LAYER 2: THE DETERMINISTIC SAFETY CIRCUIT BREAKER ---
			// Immediately bypass AI processing loop for state changes or transaction modifications
			isSensitive := strings.HasPrefix(strings.ToUpper(trimmedSQL), "UPDATE") || 
			               strings.HasPrefix(strings.ToUpper(trimmedSQL), "DELETE") || 
			               strings.HasPrefix(strings.ToUpper(trimmedSQL), "INSERT")

			if isSensitive {
				log.Println("🛡️ Circuit Breaker Triggered: Sensitive state mutation query. Passing raw query directly for safety.")
				dbConn.Write(rawPacketData)
				continue
			}

			// --- LAYER 2 & LAYER 3: SPEED PERFORMANCE TIMING & API BRAIN CALL ---
			optimizedSQL := callAIEngineWithTimeout(trimmedSQL)

			if optimizedSQL != "" && optimizedSQL != trimmedSQL {
				log.Printf("✨ AI Engine Optimization Successful! Injecting modified SQL query.")
				// Re-encode production wire-packet data containing the newly optimized SQL text
				newPacket := make([]byte, 5+len(optimizedSQL)+1)
				newPacket[0] = 'Q'
				binary.BigEndian.PutUint32(newPacket[1:5], uint32(4+len(optimizedSQL)+1))
				copy(newPacket[5:], optimizedSQL)
				newPacket[len(newPacket)-1] = 0 // Null termination character byte string seal
				dbConn.Write(newPacket)
			} else {
				// Fallback safety circuit switch active: system down, slow, or no changes detected
				dbConn.Write(rawPacketData)
			}
		} else {
			// Forward structural control data blocks straight to database loop unhindered
			dbConn.Write(rawPacketData)
		}
	}
}

func callAIEngineWithTimeout(originalSQL string) string {
	// Channel metrics interface array package to catch concurrent response streams
	responseChan := make(chan string, 1)

	go func() {
		// --- LAYER 3: THE B2B SECURITY CUSTOMER TOKEN HOOK ---
		jsonPayload := []byte(`{"query": "` + originalSQL + `", "api_key": "sk_live_misba_startup_prod"}`)
		
		req, err := http.NewRequest("POST", AIEngineURL, bytes.NewBuffer(jsonPayload))
		if err != nil {
			responseChan <- ""
			return
		}
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer sk_live_misba_startup_prod")

		client := &http.Client{Timeout: HardTimeout}
		resp, err := client.Do(req)
		if err != nil {
			responseChan <- "" // Timed out or network unavailable
			return
		}
		defer resp.Body.Close()

		buf := new(bytes.Buffer)
		buf.ReadFrom(resp.Body)
		
		// Clean out typical AI formatting markers if present
		cleanedResult := strings.ReplaceAll(buf.String(), "\"", "")
		responseChan <- strings.TrimSpace(cleanedResult)
	}()

	// --- LAYER 2: THE CRITICAL 3-MILLISECOND HARDWARE STOPWATCH SLIDE ---
	select {
	case result := <-responseChan:
		return result
	case <-time.After(HardTimeout):
		log.Println("⏳ Stopwatch Alert: AI processing crossed the 3ms limit! Activating raw query fallback path.")
		return ""
	}
}