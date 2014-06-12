# Booleans
TRUE = \x.\y.x
FALSE = \x.\y.y

# Boolean Operations
NOT = \p.\a.\b.p b a
AND = \p.\q.p q p
OR = \p.\q.p p q
IFTHENELSE = \p.\a.\b.p a b

# Pairs for list construction
PAIR = \x.\y.\f.f x y
FST = \p.p TRUE
SND = \p.p FALSE
NIL = \x.TRUE
NULL = \p.p (\x.\y.FALSE)

# Fixed point combinators
Y = \g.(\x.g (x x)) (\x.g (x x))

0 = \f.\x.x
1 = \f.\x.f x