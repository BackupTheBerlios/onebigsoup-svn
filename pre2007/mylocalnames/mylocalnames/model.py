from sqlobject import *
from turbogears.database import PackageHub

hub = PackageHub("mylocalnames")
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass

class Namespace(SQLObject):
	name = StringCol(length=40,alternateID=True,unique=True,notNone=True)
	password = StringCol(length=20,notNone=True)
	LNs = MultipleJoin("Ln")
	NSs = MultipleJoin("Ns")
	PATTERNs = MultipleJoin("Pattern")
	Xs = MultipleJoin("X")


class Ln(SQLObject):
	name = StringCol()
	url = StringCol()
	namespace = ForeignKey("Namespace")


class Ns(SQLObject):
	name = StringCol()
	url = StringCol()
	namespace = ForeignKey("Namespace")


class Pattern(SQLObject):
	name = StringCol()
	url = StringCol()
	namespace = ForeignKey("Namespace")


class X(SQLObject):
	key = StringCol()
	value = StringCol()
	namespace = ForeignKey("Namespace")

