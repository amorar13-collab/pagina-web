// === LOGICA DEL CRONOMETRO ===
let segundos = 0;
let minutos = 0;
let horas = 0;
let reloj;

document.getElementById("btn-iniciar").onclick = function() {
    clearInterval(reloj); // Evita que se duplique la velocidad
    reloj = setInterval(function() {
        segundos++;
        if (segundos == 60) {
            segundos = 0;
            minutos++;
        }
        if (minutos == 60) {
            minutos = 0;
            horas++;
        }

        // Formato rústico pero efectivo para mantener los dos ceros (00:00:00)
        let s = segundos < 10 ? "0" + segundos : segundos;
        let m = minutos < 10 ? "0" + minutos : minutos;
        let h = horas < 10 ? "0" + horas : horas;

        document.getElementById("tiempo").innerText = h + ":" + m + ":" + s;
    }, 1000);
};

document.getElementById("btn-pausar").onclick = function() {
    clearInterval(reloj);
};

document.getElementById("btn-reiniciar").onclick = function() {
    clearInterval(reloj);
    segundos = 0;
    minutos = 0;
    horas = 0;
    document.getElementById("tiempo").innerText = "00:00:00";
};


// === LOGICA DEL TRASPASO DE TEXTO ===
document.getElementById("btn-pasar").onclick = function() {
    let texto = document.getElementById("entrada").value;
    document.getElementById("salida").innerText = texto;
    document.getElementById("entrada").value = ""; // Limpia la caja
};