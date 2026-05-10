module fulladder_st(
    input a,b,c,
    output s,cout
    );
	 wire p,q,r;
xor1 x1(a,b,c,s);
and1 a1(a,b,p);
and1 a2(a,b,q);
and1 a3(a,b,r);
or1 o1(p,q,r,cout);

endmodule