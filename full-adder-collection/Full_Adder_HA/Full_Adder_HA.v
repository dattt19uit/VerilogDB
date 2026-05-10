module Full_Adder_HA(input a,b,c, output sum,carry);
wire T1,T2,T3;
HA A1(a,b,T1,T2);
HA A2(T1,c,sum,T3);
assign carry=T2|T3;

endmodule