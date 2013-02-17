with Ada.Text_IO; use Ada.Text_IO;

procedure Tasks is

	task HelloWorld;
	task body HelloWorld is
	begin
		loop
			delay 1.0;
			Put ("Hello ");
		end loop;
	end HelloWorld;

	task World;
	task body World is begin
		loop
			delay 2.0;
			Put ("world.");
		end loop;
	end World;

begin
	Put_Line ("Awesome program is runnin!");
end Tasks;
