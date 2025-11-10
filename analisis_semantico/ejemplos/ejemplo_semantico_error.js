// Ejemplo con errores semánticos: uso de variable no declarada y redeclaración
var a = 1;
a = 2; // OK

b = 3; // Uso/Asignación a variable no declarada -> semántico

var a = 4; // Redeclaración en mismo ámbito -> semántico
