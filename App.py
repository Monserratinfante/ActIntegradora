from flask import Flask, render_template, request

app = Flask(__name__)


# Ruta principal
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        alfabeto = request.form["alfabeto"]
        expresion = request.form["expresion"]
        palabra = request.form["palabra"]

        # Aquí en el futuro vas a conectar con el AFN y AFD
        resultado = f"(Simulación de procesamiento de la palabra '{palabra}')"

        return render_template(
            "index.html",
            resultado=resultado,
            alfabeto=alfabeto,
            expresion=expresion,
            palabra=palabra,
        )

    return render_template("index.html", resultado=None)


if __name__ == "__main__":
    app.run(debug=True)