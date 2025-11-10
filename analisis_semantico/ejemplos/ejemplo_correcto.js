// Ejemplo correcto - debería parsear y no producir errores semánticos
var x = 10;
let y = x + 5;

if (y > 10 && x != 0) {
    const z = y * 2 + 1;
    y = 0;
}
