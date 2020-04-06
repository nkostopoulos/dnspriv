$ORIGIN .
$TTL 86400	; 1 day
cf.example.com		IN SOA	spiderman.netmode.ece.ntua.gr. nkostopoulos.netmode.ntua.gr. (
				2020031701 ; serial
				604800     ; refresh (1 week)
				86400      ; retry (1 day)
				2419200    ; expire (4 weeks)
				86400      ; minimum (1 day)
				)
			NS	spiderman.netmode.ece.ntua.gr.
capacity.cf.example.com. IN TXT 85
buckets.cf.example.com. IN TXT 4
fingerprint.cf.example.com. IN TXT 12
0.cf.example.com. IN TXT f0e86f431773ce7fffb3b1b91406cd7c56994fa153c54edd0345ab78bda9beccd973c.a2f86387db1bfc3ba1dd5d42b0ab24da86d24466b2b6dcb31c1bd3a5645228e.9c8702bf790a1505195c358ec9a289a9d.7c83c1e45.97870dacdca0e18674dc2.e2081aadba6c7f3d9db54c3d74c5cdc7d802
1.cf.example.com. IN TXT 01833b950065fe8f53876efee76512e06bcf0c3108dd92c1e7dd902ba527305ede6b8704704a41d9e3c53294f82e162893e603f07dcbe4423bb84c65db6a3dfe7ae6376bafeeffde5d067831b7d69294d5bd3d3eda81f238da88c38008472.b53533de4bf69f93a2.8e9d96646cb6618d75581297beea1cce2.
2.cf.example.com. IN TXT ef69069cb479eff56df61e82d9ca6049293c6e888b.96b7d3cce66322ee6f192e35d41dfa5338b58743e0.10dad3d8b0fbd53b3686f1a9b0502b.cec1a9.1b31057ce8995a3c85e4785f60b457025e8d36e1b73d2.881ae51cc0a126e116bd3fc4f1ce0f.67e9f626c75bec5e36060ae6
