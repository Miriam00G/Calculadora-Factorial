from django.shortcuts import render

from .calculadora import procesar


def index(request):
    contexto = {
        "modo": "factorial",
        "expression": "",
        "valores": "",
        "pasos": None,
        "grafico": None,
        "error": None,
    }

    if request.method == "POST":
        modo = request.POST.get("modo", "factorial")
        expresion = request.POST.get("expression", "")
        valores = request.POST.get("valores", "")
        contexto.update(modo=modo, expression=expresion, valores=valores)

        try:
            modo_final, pasos, grafico = procesar(modo, expresion, valores)
            contexto.update(modo=modo_final, pasos=pasos, grafico=grafico)
        except ValueError as e:
            contexto["error"] = str(e)
        except Exception:
            contexto["error"] = (
                "Expresión no válida. Revisa los paréntesis y usa * para "
                "multiplicar."
            )

    return render(request, "factoriales/index.html", contexto)
