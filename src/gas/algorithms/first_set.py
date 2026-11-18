"""CAPÍTULO 4: ANÁLISE SINTÁTICA página 141
Defina FIRST(α), onde α é qualquer cadeia de símbolos da gramática, como sendo o conjunto de símbolos terminais que
iniciam as cadeias derivadas de α. Se α ⇒* & (ε), então & (ε) também está em FIRST(α).
Para calcular o FIRST(X) de todos os símbolos X da gramática, aplique as seguintes regras até que não haja mais termi-
nais ou & (ε) que possam ser acrescentados a algum dos conjuntos FIRST.
1. Se X é um símbolo terminal, então FIRST(X) = {X}.
2. Se X é um símbolo não-terminal e X → Y1Y2... Yk é uma produção para algum k >= 1, então acrescente a a FIRST(X)
se, para algum i, a estiver em FIRST(Yi), e & (ε) estiver em todos os FIRST(Y1),...,FIRST(Yi-1); ou seja, Y1...Yi-1 ⇒ & (ε). Se
& (ε) está em FIRST(Yj) para todo j = 1, 2, ..., k, então adicione & (ε) a FIRST(X). Por exemplo, tudo em FIRST(Y1) certa-
mente está em FIRST(X). Se Y1 não derivar & (ε), então não acrescentamos mais nada a FIRST(X), mas se Y1 ⇒ & (ε), então
adicionamos FIRST(Y2), e assim por diante.
3. Se X → & (ε) é uma produção, então acrescente & (ε) a FIRST(X).
Agora, podemos calcular FIRST para qualquer cadeia X1 X2 ... Xn da forma a seguir. Adicione a FIRST(X1X2... Xn) todos
os símbolos não-& (ε) de FIRST(X1). Inclua também os símbolos não-& (ε) de FIRST(X2), se & (ε) estiver em FIRST(X1); os símbolos não-
& (ε) de FIRST(X3), se & (ε) estiver em FIRST(X1) e em FIRST(X2); e assim por diante. Finalmente, acrescente & (ε) a FIRST(X1X2...Xn)
se, para todo i, & (ε) estiver em FIRST(Xi).
"""