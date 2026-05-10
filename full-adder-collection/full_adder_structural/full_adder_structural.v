module full_adder_structural(
    input a,
    input b,
    input c,
    output sum,
    output carry
    );
	 wire t1,t2,t3;
	 xor(sum,a,b,c);
	 and(t1,a,b);
	 and(t2,b,c);
	 and(t3,a,c);
	 or(carry,t1,t2,t3);
	 


endmodule