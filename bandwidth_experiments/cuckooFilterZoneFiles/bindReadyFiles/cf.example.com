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
