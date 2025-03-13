#!/usr/bin/python3
import os
import subprocess
import json
import re
import psutil
import logging
import cgi
form = cgi.FieldStorage()


LOG_FILE = "/var/log/fetch_services.log"

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def get_services():
    services = []
    for file in os.listdir('/etc/systemd/system'):
        if (file.startswith('FFMPEG') or file.startswith('SRT')) and file.endswith('.service'):
            name = file.replace('.service', '')
            status = get_service_status(name)
            cpu, memory = get_service_usage(name)
            stream_url = get_stream_url(name)
            stream_details = get_stream_details(stream_url) if stream_url else get_default_stream_details()

            services.append({
                'name': name,
                'status': status,
                'cpu': cpu,
                'memory': memory,
                **stream_details
            })
    return services

def get_service_status(service_name):
    return subprocess.getoutput(f'systemctl is-active {service_name}')

def get_service_usage(service_name):
    pid = subprocess.getoutput(f'systemctl show {service_name} --property=MainPID --value').strip()
    if pid and pid.isdigit():
        process = psutil.Process(int(pid))
        cpu = process.cpu_percent(interval=1)
        memory = process.memory_percent()
    else:
        cpu = "N/A"
        memory = "N/A"
    return cpu, memory

def get_stream_url(service_name):
    try:
        exec_start = subprocess.getoutput(f'systemctl show {service_name} --property=ExecStart --value').strip()
        match = re.search(r'-i\s+(".*?"|\S+)', exec_start)
        return match.group(1).strip('"') if match else None
    except Exception as e:
        logging.error(f"Error getting stream URL for {service_name}: {e}")
        return None

def get_stream_details(url):
    try:
        command = ["ffprobe", "-i", url, "-show_streams", "-select_streams", "a", "-of", "json"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        streams = json.loads(result.stdout)
        if "streams" in streams and len(streams["streams"]) > 0:
            audio_stream = streams["streams"][0]
            return {
                "codec_name": audio_stream.get("codec_name", "N/A"),
                "profile": audio_stream.get("profile", "N/A"),
                "codec_type": audio_stream.get("codec_type", "N/A"),
                "sample_rate": audio_stream.get("sample_rate", "N/A"),
                "channels": audio_stream.get("channels", "N/A"),
                "channel_layout": audio_stream.get("channel_layout", "N/A"),
                "bit_rate": audio_stream.get("bit_rate", "N/A"),
            }
        return get_default_stream_details()
    except Exception as e:
        logging.error(f"Error getting stream details for {url}: {e}")
        return get_default_stream_details()

def get_default_stream_details():
    return {
        "codec_name": "N/A",
        "profile": "N/A",
        "codec_type": "N/A",
        "sample_rate": "N/A",
        "channels": "N/A",
        "channel_layout": "N/A",
        "bit_rate": "N/A"
    }

def perform_action(service, action):
    if action in ['start', 'stop', 'restart']:
        command = ['sudo', '/usr/local/bin/ffmpeg_service_control.sh', service, action]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {"success": True, "action": action, "service": service}
    return {"success": False, "error": "Invalid action"}

def main():
    print("Content-Type: application/json\n")
    form = cgi.FieldStorage()
    action = form.getvalue("action")
    service = form.getvalue("service")

    if action and service:
        result = perform_action(service, action)
        print(json.dumps(result))
    else:
        services = get_services()
        print(json.dumps({'services': services}))

if __name__ == '__main__':
    main()
