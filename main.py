#!/usr/bin/env python3
from flask import Flask, render_template, jsonify 
import subprocess
import os
import json

app = Flask(__name__)

PC_MAC_ADDRESS = os.environ.get("PC_MAC_ADDRESS", "AA:BB:CC:DD:EE:FF")
PC_NAME = os.environ.get("PC_NAME", "Gaming PC")

@app.route('/')
def index():
    return render_template('index.html', pc_name=PC_NAME)

@app.route('/manifest.json')
def manifest():
    manifest_data = {
        "name": "Wake on LAN",
        "short_name": "WoL",
        "description": "Wake your PC remotely via VPN",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f5f5f5",
        "theme_color": "#007AFF",
        "icons": [
            {
                "src": "/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest_data)

@app.route('/sw.js')
def service_worker():
    sw_content = '''
const CACHE_NAME = 'wol-v1';
const urlsToCache = [
    '/',
    '/manifest.json'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});
'''
    return sw_content, 200, {'Content-Type': 'application/javascript'}

@app.route('/icon-192.png')
def icon_192():
    svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
        <rect width="192" height="192" fill="#007AFF" rx="24"/>
        <text x="96" y="120" font-family="Arial" font-size="80" fill="white" text-anchor="middle">🖥️</text>
    </svg>'''
    return svg_icon, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/icon-512.png')
def icon_512():
    svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
        <rect width="512" height="512" fill="#007AFF" rx="64"/>
        <text x="256" y="320" font-family="Arial" font-size="200" fill="white" text-anchor="middle">🖥️</text>
    </svg>'''
    return svg_icon, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/wake', methods=['POST'])
def wake_pc():
    try:
        print(f"Sending wake signal to {PC_NAME} with MAC address {PC_MAC_ADDRESS}")
        result = subprocess.run(['wakeonlan', PC_MAC_ADDRESS], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': f'Wake signal sent to {PC_NAME}!'
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'Error: {result.stderr}'
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)