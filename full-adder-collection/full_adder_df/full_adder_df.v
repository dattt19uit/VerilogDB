module full_adder_df(a,b,c,sum);

	input a,b,c;
	output sum;

	assign sum=a ^ b ^ c;
	//assign carry= (a&b)|(b&c)|(c&a);

endmodule