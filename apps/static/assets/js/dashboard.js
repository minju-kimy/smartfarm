console.log("dashboard.js loaded");
document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const deviceStates = {
        fan: false,
        led: false,
        pump: false,
        co2: false,
        motor1: 'stop',
        motor2: 'stop',
        ec: false,
        ph: false,
        water_solenoid: false,
        nutrient_pump: false
    };

    socket.emit('get_latest_sensor_data');

    // Device toggle buttons
    document.querySelectorAll('.toggle-device').forEach(button => {
        button.addEventListener('click', function() {
            const device = this.dataset.device;
            
            // EC와 PH 버튼 상호 배타적 처리
            if (device === 'ec' || device === 'ph') {
                if (device === 'ec' && deviceStates.ph) {
                    // PH가 켜져있을 때 EC를 켜면 PH를 끄기
                    deviceStates.ph = false;
                    socket.emit('toggle_device', { device: 'ph', state: false });
                    updateDeviceState('ph', false);
                } else if (device === 'ph' && deviceStates.ec) {
                    // EC가 켜져있을 때 PH를 켜면 EC를 끄기
                    deviceStates.ec = false;
                    socket.emit('toggle_device', { device: 'ec', state: false });
                    updateDeviceState('ec', false);
                }
            }
            
            deviceStates[device] = !deviceStates[device];
            // Socket.IO로 서버에 알림
            socket.emit('toggle_device', { device: device, state: deviceStates[device] });
            // MQTT 메시지 전송
            fetch(toggleUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: device,
                    state: deviceStates[device]
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('MQTT message sent:', data);
            })
            .catch(error => {
                console.error('Error sending MQTT message:', error);
            });
            updateDeviceState(device, deviceStates[device]);
        });
    });

    // Motor control buttons
    document.querySelectorAll('.motor-control').forEach(button => {
        button.addEventListener('click', function() {
            const device = this.dataset.device;
            const state = this.dataset.state;
            deviceStates[device] = state;
            // Socket.IO로 서버에 알림
            socket.emit('toggle_device', { device: device, state: state });
            // MQTT 메시지 전송
            fetch(toggleUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: device,
                    state: state
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('MQTT message sent:', data);
            })
            .catch(error => {
                console.error('Error sending MQTT message:', error);
            });
            updateDeviceState(device, state);
        });
    });

    // Update device state display
    function updateDeviceState(device, state) {
        const stateText = document.getElementById(`${device}StateText`);
        if (device === 'motor1' || device === 'motor2') {
            stateText.textContent = state.toUpperCase();
        } else {
            stateText.textContent = state ? 'ON' : 'OFF';
            // Update button text
            const button = document.querySelector(`[data-device="${device}"]`);
            if (button) {
                button.textContent = state ? 'Turn OFF' : 'Turn ON';
                button.classList.toggle('btn-primary', !state);
                button.classList.toggle('btn-danger', state);
            }
        }
    }

    // Handle sensor data updates
    socket.on('sensor_update', function(data) {
        document.getElementById('temperature').textContent = data.temperature || '--';
        document.getElementById('humidity').textContent = data.humidity || '--';
        document.getElementById('co2').textContent = data.co2 || '--';
        document.getElementById('ec').textContent = data.ec || '--';
        document.getElementById('ph').textContent = data.ph || '--';
    });

    // Handle device state updates
    socket.on('device_update', function(data) {
        const { device, state } = data;
        deviceStates[device] = state;
        updateDeviceState(device, state);
    });

    // Handle sensor history updates
    socket.on('sensor_history', function(data) {
        const tbody = document.getElementById('sensorHistory');
        tbody.innerHTML = '';
        data.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(record.timestamp).toLocaleString()}</td>
                <td>${record.temperature || '--'}</td>
                <td>${record.humidity || '--'}</td>
                <td>${record.co2 || '--'}</td>
                <td>${record.ec || '--'}</td>
                <td>${record.ph || '--'}</td>
            `;
            tbody.appendChild(row);
        });
    });

    // Initialize button states
    Object.keys(deviceStates).forEach(device => {
        if (device !== 'motor1' && device !== 'motor2') {
            const button = document.querySelector(`[data-device="${device}"]`);
            if (button) {
                button.textContent = deviceStates[device] ? 'Turn OFF' : 'Turn ON';
                button.classList.toggle('btn-danger', deviceStates[device]);
                button.classList.toggle('btn-primary', !deviceStates[device]);
            }
        }
    });
}); 