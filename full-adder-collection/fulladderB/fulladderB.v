module fulladderB(sum,carry,A,B,Cin
    );
input wire A,B,Cin;
output reg sum,carry;
always @(A or B or Cin)
begin
sum=A^B^Cin;
carry=((A&B)|(B&Cin)|(Cin&A));
end

endmodule