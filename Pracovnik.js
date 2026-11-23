class Pracovnik {
    // Súkromné vlastnosti.
    #id;
    #meno;
    #oddelenie;
    #aktivny;

    // Konštruktor s predvolenými hodnotami.
    constructor(
        id = 0,
        meno = "",
        oddelenie = "IT",
        aktivny = true
    ) {
        this.#id = id;
        this.#meno = meno;
        this.#oddelenie = oddelenie;
        this.#aktivny = aktivny;
    }

    // ID sa dá zvonka iba čítať.
    get id() {
        return this.#id;
    }

    get meno() {
        return this.#meno;
    }

    set meno(hodnota) {
        this.#meno = hodnota;
    }

    get oddelenie() {
        return this.#oddelenie;
    }

    set oddelenie(hodnota) {
        this.#oddelenie = hodnota;
    }

    get aktivny() {
        return this.#aktivny;
    }

    set aktivny(hodnota) {
        this.#aktivny = hodnota;
    }

    // Vytvorí samostatnú kópiu pracovníka.
    kopia() {
        return new Pracovnik(
            this.#id,
            this.#meno,
            this.#oddelenie,
            this.#aktivny
        );
    }

    // Určí podobu objektu pri JSON.stringify().
    toJSON() {
        return {
            id: this.#id,
            meno: this.#meno,
            oddelenie: this.#oddelenie,
            aktivny: this.#aktivny
        };
    }

    // Z obyčajného objektu vytvorí inštanciu triedy.
    static zObjektu(objekt) {
        return new Pracovnik(
            objekt.id,
            objekt.meno,
            objekt.oddelenie,
            objekt.aktivny
        );
    }
}