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
0.cf.example.com. IN TXT f0e86f431773
1.cf.example.com. IN TXT ce7fffb3b1b9
2.cf.example.com. IN TXT 1406cd7c5699
3.cf.example.com. IN TXT 4fa153c54edd
4.cf.example.com. IN TXT 0345ab78bda9
5.cf.example.com. IN TXT beccd973c
6.cf.example.com. IN TXT a2f86387db1b
7.cf.example.com. IN TXT fc3ba1dd5d42
8.cf.example.com. IN TXT b0ab24da86d2
9.cf.example.com. IN TXT 4466b2b6dcb3
10.cf.example.com. IN TXT 1c1bd3a56452
11.cf.example.com. IN TXT 28e
12.cf.example.com. IN TXT 9c8702bf790a
13.cf.example.com. IN TXT 1505195c358e
14.cf.example.com. IN TXT c9a289a9d
15.cf.example.com. IN TXT 7c83c1e45
16.cf.example.com. IN TXT 97870dacdca0
17.cf.example.com. IN TXT e18674dc2
18.cf.example.com. IN TXT e2081aadba6c
19.cf.example.com. IN TXT 7f3d9db54c3d
20.cf.example.com. IN TXT 74c5cdc7d802
21.cf.example.com. IN TXT beedbca27da3
22.cf.example.com. IN TXT 01833b950065
23.cf.example.com. IN TXT fe8f53876efe
24.cf.example.com. IN TXT e76512e06bcf
25.cf.example.com. IN TXT 0c3108dd92c1
26.cf.example.com. IN TXT e7dd902ba527
27.cf.example.com. IN TXT 305ede6b8704
28.cf.example.com. IN TXT 704a41d9e3c5
29.cf.example.com. IN TXT 3294f82e1628
30.cf.example.com. IN TXT 93e603f07dcb
31.cf.example.com. IN TXT e4423bb84c65
32.cf.example.com. IN TXT db6a3dfe7ae6
33.cf.example.com. IN TXT 376bafeeffde
34.cf.example.com. IN TXT 5d067831b7d6
35.cf.example.com. IN TXT 9294d5bd3d3e
36.cf.example.com. IN TXT da81f238da88
37.cf.example.com. IN TXT c38008472
38.cf.example.com. IN TXT b53533de4bf6
39.cf.example.com. IN TXT 9f93a2
40.cf.example.com. IN TXT 8e9d96646cb6
41.cf.example.com. IN TXT 618d75581297
42.cf.example.com. IN TXT beea1cce2
43.cf.example.com. IN TXT 8a263f5aabc4
44.cf.example.com. IN TXT ef69069cb479
45.cf.example.com. IN TXT eff56df61e82
46.cf.example.com. IN TXT d9ca6049293c
47.cf.example.com. IN TXT 6e888b
48.cf.example.com. IN TXT 96b7d3cce663
49.cf.example.com. IN TXT 22ee6f192e35
50.cf.example.com. IN TXT d41dfa5338b5
51.cf.example.com. IN TXT 8743e0
52.cf.example.com. IN TXT 10dad3d8b0fb
53.cf.example.com. IN TXT d53b3686f1a9
54.cf.example.com. IN TXT b0502b
55.cf.example.com. IN TXT cec1a9
56.cf.example.com. IN TXT 1b31057ce899
57.cf.example.com. IN TXT 5a3c85e4785f
58.cf.example.com. IN TXT 60b457025e8d
59.cf.example.com. IN TXT 36e1b73d2
60.cf.example.com. IN TXT 881ae51cc0a1
61.cf.example.com. IN TXT 26e116bd3fc4
62.cf.example.com. IN TXT f1ce0f
63.cf.example.com. IN TXT 67e9f626c75b
64.cf.example.com. IN TXT ec5e36060ae6
65.cf.example.com. IN TXT 7431481ffb8c
66.cf.example.com. IN TXT 38b60b42c641
67.cf.example.com. IN TXT d1acdcd80255
69.cf.example.com. IN TXT c62fd6e6a
70.cf.example.com. IN TXT e96806f3df05
71.cf.example.com. IN TXT d9de68
72.cf.example.com. IN TXT 0116a2ee0f09
73.cf.example.com. IN TXT 1c3260e047c1
74.cf.example.com. IN TXT c931422a27b5
75.cf.example.com. IN TXT bcdb2ab20bc1
76.cf.example.com. IN TXT b3c0ae26f205
77.cf.example.com. IN TXT 3bbd264bac63
78.cf.example.com. IN TXT dc3571b34
79.cf.example.com. IN TXT 4edb58712
80.cf.example.com. IN TXT 864f9f
81.cf.example.com. IN TXT f1103d
82.cf.example.com. IN TXT 9bb9f0a099f8
83.cf.example.com. IN TXT ef55c73d3cdc
84.cf.example.com. IN TXT 03d2b0e16
