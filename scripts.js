async function fetchServices() {
    try {
        const response = await fetch('/cgi-bin/fetch_services.py');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        populateTable(data.services);
    } catch (error) {
        console.error('Error fetching services:', error);
    }
}

function populateTable(services) {
    const tableBody = document.getElementById('service-data');
    tableBody.innerHTML = ''; // Clear existing rows

    services.forEach(service => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${service.name}</td>
            <td>${service.status}</td>
            <td>${service.cpu}%</td>
            <td>${service.memory}%</td>
            <td>${service.codec_name}</td>
            <td>${service.profile}</td>
            <td>${service.codec_type}</td>
            <td>${service.sample_rate}</td>
            <td>${service.channels}</td>
            <td>${service.channel_layout}</td>
            <td>${service.bit_rate}</td>
            <td>
                <button onclick="performAction('${service.name}', 'start')">Start</button>
                <button onclick="performAction('${service.name}', 'stop')">Stop</button>
                <button onclick="performAction('${service.name}', 'restart')">Restart</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

async function performAction(service, action) {
    try {
        const response = await fetch(`/cgi-bin/fetch_services.py?action=${action}&service=${service}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const result = await response.json();
        if (result.success) {
            alert(`Service ${service} ${action}ed successfully!`);
            fetchServices(); // Refresh the table
        } else {
            alert(`Failed to ${action} service ${service}: ${result.error}`);
        }
    } catch (error) {
        console.error('Error performing action:', error);
    }
}

setInterval(fetchServices, 5000);

window.onload = fetchServices;
