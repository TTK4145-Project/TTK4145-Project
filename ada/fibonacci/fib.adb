with Ada.Text_IO;
with Ada.Integer_Text_IO;
use Ada.Text_IO;
use Ada.Integer_Text_IO;

procedure Fib is
	N : Integer;

	function Fibonacci (N: Integer) return Integer is
		tmp1 : Integer := 0;
		tmp2 : Integer := 1;	

		result : Integer := 0;
	begin
		result := tmp1 + tmp2;

		for i in 1 .. n-2 loop
			tmp1 := tmp2;
			tmp2 := result;
			result := tmp1 + tmp2;
		end loop;

		return result;
	end Fibonacci;
begin
	Put("What Fibonacci number would you like to see? ");

	begin
		Get(N);
	exception when Data_Error => 
		Ada.Text_IO.Put ("Kun tall er lov");
	end;

	Put (Fibonacci(N));
end Fib;
