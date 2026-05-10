module Fulladder_behavioural(a,b,c,sum,carry);
input a,b,c;
output sum,carry;
reg sum,carry;
always@(a,b,c)
begin
sum=a^b^c;
carry=(a&b)|(b&c)|(c&a);
end
endmodule