module full_adder(rst,a,b,cin,sum,cout);
input rst;
input a,b,cin;
output reg sum,cout;

always @(*)
    begin
      if(rst==1)
        {sum,cout}=0;
      else  
        begin
          sum=a^b^cin;
          cout=((a&b)|(b&cin)|(a&cin));
        end
    end
endmodule