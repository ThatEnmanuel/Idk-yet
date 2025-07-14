// 🪖 HARDWARE MONITOR - TACTICAL OPS
// Military JavaScript Implementation

class MilitaryMonitor {
    constructor() {
        this.missionStartTime = new Date();
        this.updateInterval = 3000; // 3 seconds
        this.alertThresholds = {
            cpu: 80,
            memory: 85,
            disk: 90
        };
        this.systemStatus = 'OPERATIONAL';
        this.authToken = null;
        this.missionLogs = [];
        
        // Military color scheme
        this.militaryColors = {
            success: '#00FF41',
            warning: '#FFBF00',
            danger: '#FF073A',
            tactical: '#FF6B35',
            alert: '#FFD23F'
        };
        
        console.log('🪖 TACTICAL OPS INITIALIZED');
    }
    
    // Initialize military operations
    async init() {
        try {
            await this.authenticate();
            this.updateMissionTime();
            this.updateSystemStatus();
            this.addMissionLog('INFO', 'TACTICAL OPS INITIALIZED');
            this.addMissionLog('INFO', 'HARDWARE SCAN IN PROGRESS');
            
            // Start mission timer
            setInterval(() => this.updateMissionTime(), 1000);
            
            // Start data updates
            setInterval(() => this.updateTacticalData(), this.updateInterval);
            
            // Initial data load
            await this.updateTacticalData();
            
        } catch (error) {
            this.addMissionLog('ERROR', `MISSION INITIALIZATION FAILED: ${error.message}`);
            this.triggerDefconAlert('SYSTEM OFFLINE - AUTHENTICATION FAILED');
        }
    }
    
    // Military authentication
    async authenticate() {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: 'admin',
                    password: 'admin'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.authToken = data.access_token;
                this.addMissionLog('INFO', 'AUTHENTICATION SUCCESSFUL');
                return true;
            } else {
                throw new Error('Authentication failed');
            }
        } catch (error) {
            this.addMissionLog('ERROR', `AUTHENTICATION ERROR: ${error.message}`);
            throw error;
        }
    }
    
    // Update mission time display
    updateMissionTime() {
        const now = new Date();
        const elapsed = new Date(now - this.missionStartTime);
        const hours = elapsed.getUTCHours().toString().padStart(2, '0');
        const minutes = elapsed.getUTCMinutes().toString().padStart(2, '0');
        const seconds = elapsed.getUTCSeconds().toString().padStart(2, '0');
        
        const missionTimeElement = document.getElementById('mission-time');
        if (missionTimeElement) {
            missionTimeElement.textContent = `${hours}:${minutes}:${seconds}`;
        }
    }
    
    // Update system status
    async updateSystemStatus() {
        try {
            const response = await fetch('/api/mission-status', {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.systemStatus = data.mission_status;
                
                const statusElement = document.getElementById('system-status');
                if (statusElement) {
                    statusElement.textContent = this.systemStatus;
                    statusElement.className = `system-status ${this.systemStatus.toLowerCase()}`;
                }
                
                // Update alert level
                if (data.alert_level) {
                    this.updateAlertLevel(data.alert_level);
                }
            }
        } catch (error) {
            this.addMissionLog('WARNING', `STATUS UPDATE FAILED: ${error.message}`);
        }
    }
    
    // Update tactical data (hardware metrics)
    async updateTacticalData() {
        try {
            const response = await fetch('/api/stats', {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateGauges(data);
                this.checkAlertThresholds(data);
                this.addMissionLog('INFO', 'TACTICAL DATA UPDATED');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            this.addMissionLog('ERROR', `DATA UPDATE FAILED: ${error.message}`);
            this.triggerDefconAlert('DATA ACQUISITION FAILED');
        }
    }
    
    // Update military gauges
    updateGauges(data) {
        // CPU Gauge
        if (data.cpu && data.cpu.usage !== undefined) {
            this.updateGauge('cpu', data.cpu.usage);
        }
        
        // Memory Gauge
        if (data.ram && data.ram.usage !== undefined) {
            this.updateGauge('memory', data.ram.usage);
        }
        
        // Disk Gauge
        if (data.disk && data.disk.usage !== undefined) {
            this.updateGauge('disk', data.disk.usage);
        }
        
        // Network Data
        if (data.network) {
            this.updateNetworkData(data.network);
        }
    }
    
    // Update individual gauge
    updateGauge(type, value) {
        const needle = document.getElementById(`${type}-needle`);
        const valueElement = document.getElementById(`${type}-value`);
        
        if (needle && valueElement) {
            // Calculate needle angle (-120 to 120 degrees)
            const angle = (value / 100) * 240 - 120;
            needle.style.transform = `translate(-50%, -100%) rotate(${angle}deg)`;
            
            // Update value display
            valueElement.textContent = `${Math.round(value)}%`;
            
            // Update needle color based on threshold
            if (value > this.alertThresholds[type]) {
                needle.style.background = this.militaryColors.danger;
                this.triggerDefconAlert(`${type.toUpperCase()} CRITICAL: ${Math.round(value)}%`);
            } else if (value > this.alertThresholds[type] * 0.7) {
                needle.style.background = this.militaryColors.warning;
        } else {
                needle.style.background = this.militaryColors.success;
            }
        }
    }
    
    // Update network data
    updateNetworkData(networkData) {
        const sentElement = document.getElementById('network-sent');
        const receivedElement = document.getElementById('network-received');
        
        if (sentElement && networkData.sent_mb !== undefined) {
            sentElement.textContent = `${networkData.sent_mb.toFixed(1)} MB`;
        }
        
        if (receivedElement && networkData.received_mb !== undefined) {
            receivedElement.textContent = `${networkData.received_mb.toFixed(1)} MB`;
        }
    }
    
    // Check alert thresholds
    checkAlertThresholds(data) {
        if (data.cpu && data.cpu.usage > this.alertThresholds.cpu) {
            this.addMissionLog('WARNING', `CPU THRESHOLD EXCEEDED: ${data.cpu.usage}%`);
        }
        
        if (data.ram && data.ram.usage > this.alertThresholds.memory) {
            this.addMissionLog('WARNING', `MEMORY THRESHOLD EXCEEDED: ${data.ram.usage}%`);
        }
        
        if (data.disk && data.disk.usage > this.alertThresholds.disk) {
            this.addMissionLog('WARNING', `DISK THRESHOLD EXCEEDED: ${data.disk.usage}%`);
        }
    }
    
    // Add mission log
    async addMissionLog(level, message) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp: timestamp,
            level: level,
            message: message
        };
        
        this.missionLogs.push(logEntry);
        
        // Keep only last 50 logs
        if (this.missionLogs.length > 50) {
            this.missionLogs = this.missionLogs.slice(-50);
        }
        
        // Update log display
        this.updateLogDisplay();
        
        // Send to backend if authenticated
        if (this.authToken) {
            try {
                await fetch('/api/mission-logs/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.authToken}`
                    },
                    body: JSON.stringify({
                        level: level,
                        message: message
                    })
                });
            } catch (error) {
                console.error('Failed to send log to backend:', error);
            }
        }
    }
    
    // Update log display
    updateLogDisplay() {
        const logOutput = document.getElementById('log-output');
        if (logOutput) {
            logOutput.innerHTML = '';
            
            this.missionLogs.slice(-20).forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = `log-entry ${log.level.toLowerCase()}`;
                
                const time = new Date(log.timestamp).toLocaleTimeString();
                logEntry.textContent = `[${time}] ${log.level}: ${log.message}`;
                
                logOutput.appendChild(logEntry);
            });
            
            // Auto-scroll to bottom
            logOutput.scrollTop = logOutput.scrollHeight;
        }
    }
    
    // Trigger DEFCON alert
    triggerDefconAlert(message) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-defcon');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert-defcon';
        alertDiv.textContent = `⚠️ DEFCON ALERT: ${message}`;
        
        // Insert at top of command center
        const commandCenter = document.querySelector('.command-center');
        if (commandCenter) {
            commandCenter.insertBefore(alertDiv, commandCenter.firstChild);
        }
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 10000);
        
        this.addMissionLog('ALERT', message);
    }
    
    // Update alert level display
    updateAlertLevel(alertLevel) {
        // You can add visual indicators for DEFCON levels here
        console.log(`ALERT LEVEL: ${alertLevel}`);
    }
}

// Initialize military monitor when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🪖 INITIALIZING TACTICAL OPS...');
    
    const militaryMonitor = new MilitaryMonitor();
    militaryMonitor.init().catch(error => {
        console.error('MISSION FAILED:', error);
        document.body.innerHTML = `
            <div style="
                background: #0D1117; 
                color: #FF073A; 
                font-family: 'JetBrains Mono', monospace; 
                padding: 2rem; 
                text-align: center;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            ">
                <h1>🪖 MISSION FAILED</h1>
                <p>SYSTEM OFFLINE - AUTHENTICATION ERROR</p>
                <p>${error.message}</p>
                <button onclick="location.reload()" style="
                    background: #4A5D23; 
                    color: #FFD23F; 
                    border: 2px solid #FFD23F; 
                    padding: 1rem 2rem; 
                    font-family: 'JetBrains Mono', monospace; 
                    font-weight: 700; 
                    text-transform: uppercase; 
                    cursor: pointer;
                    margin-top: 2rem;
                ">RETRY MISSION</button>
            </div>
        `;
    });
}); 