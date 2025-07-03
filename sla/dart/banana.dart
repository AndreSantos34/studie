void main() {

Filme filme = Filme("Flow", 80, true);
filme.imprime();

}

class Filme {
String nome=''; 
int duracao = 0;
bool oscar = false;

Filme(this.nome, this.duracao, this.oscar);

void imprime(){
    print('Nome: $nome - Duração(min): $duracao - Oscar: $oscar');
}

}
