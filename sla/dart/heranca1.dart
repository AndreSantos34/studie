void main() {
Carro carro = Carro("Uno", 60);
carro.ImprimeDados();

Passeio passeio = Passeio("Onix", 116);
passeio.ImprimeDados();
print(passeio.ConverteParaWatts().toString()+"W");

Esportivo esportivo = Esportivo("M3", 510);
esportivo.ImprimeDados();
print (esportivo.ConverteParaWatts().toString()+"W");
}


class Carro {
    String modelo = "";
    int potencia = 0;

    Carro(this.modelo, this.potencia);
void ImprimeDados (){
    print("Carro.\nModelo: " + modelo + "Potencia: " + potencia.toString());
}
}


class Passeio extends Carro {
    Passeio(String model, int power) : super(model, power);

    void ImprimeDados(){
        print ("Modelo: " + modelo + "Potencia em cv: " + potencia.toString());
    
    }

    int ConverteParaWatts(){
        return potencia * 735;
      
    }
}

class Esportivo extends Carro{
    Esportivo(String mod, int pot) : super(mod, pot);

    void ImprimeDados(){
        print("Carro de Luxo.\nModelo: "+ modelo +"potencia em HP : " + potencia.toString());
    }
    int ConverteParaWatts() {
        return potencia * 746;
        
    }
}

