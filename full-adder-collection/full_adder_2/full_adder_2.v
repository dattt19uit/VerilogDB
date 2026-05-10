module full_adder_2  (input a, b, cin, output s_out, c_out);

 wire s, c0, c1;
 half_addr HA1 (a, b, s, c0);
 half_addr HA2 (s, cin, s_out, c1);
 
 assign c_out = c0 | c1;
endmodule