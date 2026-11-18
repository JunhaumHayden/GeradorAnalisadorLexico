"""CAPÍTULO 4: ANÁLISE SINTÁTICA página 141
Defina FOLLOW(A), para o não-terminal A, como sendo o conjunto de terminais a que podem aparecer imediatamente
à direita de A em alguma forma sentencial; ou seja, o conjunto de terminais a tais que exista uma derivação na forma S ⇒ αAaβ, para algum α e β. Observe que pode haver símbolos entre A e a, em algum momento durante a derivação, mas, nesse caso, eles derivaram & (ε) e desapareceram. Além disso, se A for o símbolo não-terminal mais à direita em alguma forma sentencial, então $ estará em FOLLOW(A); lembre-se de que $ é um símbolo “marcador de fim da cadeia de entrada”, e, como tal, não faz parte de nenhuma gramática.
Para calcular o FOLLOW(A) para todos os não-terminais A, aplique as seguintes regras até que nada mais possa ser acrescentado a nenhum dos conjuntos FOLLOW:
1. Coloque $ em FOLLOW(S), onde S é o símbolo inicial da gramática, e $ é o marcador de fim da entrada ou fim de arquivo.
2. Se houver uma produção A → αBβ, então tudo em FIRST(β) exceto & (ε) está em FOLLOW(B).
3. Se houver uma produção A → αB, ou uma produção A → αBβ, onde o FIRST(β) contém & (ε), então inclua o FOLLOW(A) em FOLLOW(B).
"""