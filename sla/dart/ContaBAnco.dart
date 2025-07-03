void main(){
Conta conta = Conta("Adam Sandler", 1000, false, 5);

conta.ImprimeDadosCorretista();
conta.CalculaMontante();

Poupanca pop = Poupanca ("Juca", 1200, true, 12.5 );
pop.ImprimeDadosCorretista();
pop.CalculaMontante();

AltoRisco ar = AltoRisco("chico", 54321, true, 3.4);
ar.CalculaMontante();
ar.ImprimeDadosCorretista();
}

class Conta {
String correntista = '';
double saldo = 0;
bool limite = false;
double taxa = 0;

Conta(this.correntista, this.saldo, this.limite, this.taxa);

void ImprimeDadosCorretista() => print ('$correntista \n $saldo \n $limite \n $taxa');

void CalculaMontante() {
print ('${saldo * (1+ (taxa/100) )}');

}
}

class Poupanca extends Conta {
    Poupanca(String nome, double saldo, bool limite, double taxa) : super(nome, saldo, limite, taxa);

    @override
    void ImprimeDadosCorretista(){
        print('Nome: $correntista  Saldo: $saldo  Limite: $limite Taxa: $taxa' );

    }
    
        @override
        void CalculaMontante(){
            print ('${saldo * (1+ (taxa/100) ) + 0.99}');
        }
}

class AltoRisco extends Conta {
    AltoRisco(String nome, double saldo, bool limite, double taxa) : super(nome, saldo, limite, taxa);}