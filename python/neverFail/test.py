import package_manager
from redundancy import redundancy

buf = []
manager = package_manager.package_manager(buf)
print manager.raw_parse(redundancy.package_start)
print manager.raw_parse(redundancy.messages['client_request']+"hallllooooo")
print manager.raw_parse("hallllooooo"+redundancy.package_end)
print manager.raw_parse(redundancy.package_start)
print manager.raw_parse(redundancy.messages['client_request']+"hallllooooo")
print manager.raw_parse("hallllooooo"+redundancy.package_end)
print manager.raw_parse(redundancy.messages['client_request']+"hallllooooo")
print manager.raw_parse(redundancy.package_start)
print manager.raw_parse(redundancy.messages['client_request']+"hallllooooo")
print manager.raw_parse("hallllooooo"+redundancy.package_end)
for package in buf:
	print package.pack()

