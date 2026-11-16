#!/usr/bin/env python3
"""Minimal MQTT 3.1.1 dumper for Venus OS. usage: mq.py host seconds out.json [topicfilter]
Only publishes the Venus read-only keepalive request (R/<id>/keepalive)."""
import socket, struct, sys, time, json
host, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
filt = sys.argv[4] if len(sys.argv) > 4 else 'N/#'
def s(b): return struct.pack('>H', len(b)) + b
def rl(n):
    o = b''
    while True:
        d = n % 128; n //= 128
        o += bytes([d | (0x80 if n else 0)])
        if not n: return o
def pkt(t, body): return bytes([t]) + rl(len(body)) + body
sk = socket.create_connection((host, 1883), 5)
sk.sendall(pkt(0x10, s(b'MQTT') + b'\x04\x02' + struct.pack('>H', 60) + s(b'batsync-dump-%d' % (time.time() % 100000))))
sk.sendall(pkt(0x82, b'\x00\x01' + s(filt.encode()) + b'\x00'))
buf = b''; vals = {}; log = []; portal = None; t0 = time.time(); lastka = 0
sk.settimeout(0.5)
while time.time() - t0 < secs:
    if portal and time.time() - lastka > 20:
        sk.sendall(pkt(0x30, s(('R/%s/keepalive' % portal).encode()))); lastka = time.time()
    try:
        d = sk.recv(65536)
        if not d: break
        buf += d
    except socket.timeout:
        pass
    while len(buf) >= 2:
        n = 0; i = 1; sh = 0
        while True:
            if i >= len(buf): n = None; break
            b = buf[i]; n |= (b & 127) << sh; sh += 7; i += 1
            if not b & 128: break
        if n is None or len(buf) < i + n: break
        h, body, buf = buf[0], buf[i:i + n], buf[i + n:]
        if h >> 4 == 3:
            tl = struct.unpack('>H', body[:2])[0]; topic = body[2:2 + tl].decode(); pl = body[2 + tl:]
            p = topic.split('/')
            if not portal and len(p) > 1 and p[0] == 'N': portal = p[1]
            try: v = json.loads(pl).get('value') if pl else None
            except Exception: v = pl.decode(errors='replace')
            vals[topic] = v; log.append((round(time.time() - t0, 2), topic, v))
json.dump({'vals': vals, 'log': log}, open(out, 'w'))
print('portal', portal, 'topics', len(vals), 'msgs', len(log))
