module fulladder_subtractor(a,b,c,ctrl,sum,carry,diff,borrow);
input a,b,c;
input ctrl;
output reg sum,carry,diff,borrow;
always @(*)
begin
    if(ctrl==0)
    begin
        sum=a^b^c;
        carry=(a&b)|(b&c)|(c&a);
        diff=0;borrow=0;
    end
    else
    begin
        diff=a^b^c;
        borrow=c&(a~^b)|(~a&b);
        sum=0;carry=0;
        end
end
        


endmodule