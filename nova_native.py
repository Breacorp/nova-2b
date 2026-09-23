"""
Nova Native Math & Packing — Aritmética 100% Entera y Ternaria {-1, 0, +1}
Desarrollado por ModernoTech.

REGLAS ESTRICTAS:
- Prohibido el uso de float, float32, float64, double, math.sqrt, math.exp.
- Pesos ternarios: W ∈ {-1, 0, +1}.
- Empaquetamiento ternario de 2 bits por peso: 4 pesos por byte.
    00 ->  0
    01 -> +1
    10 -> -1
    11 -> reservado
- Escalares en punto fijo (Base 1000): 1000 = 100.0%, 850 = 85.0%, etc.
- Activaciones: Int16 [-32768, 32767].
- Acumuladores: Int32.
"""

from typing import List, Tuple

SCALE_BASE = 1000  # Escala de punto fijo entero para porcentajes y métricas

# ============================================================================
# 1. EMPAQUETAMIENTO TERNARIO (2 bits / peso -> 4 pesos / byte)
# ============================================================================

def pack_ternary(weights: List[int]) -> bytes:
    """
    Empaqueta una lista de pesos ternarios {-1, 0, +1} en bytes.
    Cada peso ocupa 2 bits:
      0  -> 0b00 (0)
     +1  -> 0b01 (1)
     -1  -> 0b10 (2)
    """
    packed = bytearray()
    for i in range(0, len(weights), 4):
        chunk = weights[i:i+4]
        byte_val = 0
        for idx, w in enumerate(chunk):
            if w == 0:
                bits = 0b00
            elif w == 1:
                bits = 0b01
            elif w == -1:
                bits = 0b10
            else:
                raise ValueError(f"Peso no ternario: {w}. Debe ser -1, 0 o +1.")
            byte_val |= (bits << (idx * 2))
        packed.append(byte_val)
    return bytes(packed)

def unpack_ternary(packed_bytes: bytes, num_weights: int) -> List[int]:
    """
    Desempaqueta bytes en una lista de enteros ternarios {-1, 0, +1}.
    """
    weights = []
    bit_to_val = {0b00: 0, 0b01: 1, 0b10: -1, 0b11: 0}
    for b in packed_bytes:
        for shift in (0, 2, 4, 6):
            if len(weights) < num_weights:
                bits = (b >> shift) & 0b11
                weights.append(bit_to_val[bits])
    return weights

# ============================================================================
# 2. PRODUCTO INTERNO Y CONVOLUCIÓN 100% ENTERA
# ============================================================================

def dot_product_ternary(packed_weights: bytes, num_weights: int, activations: List[int]) -> int:
    """
    Calcula producto punto sin multiplicaciones de coma flotante.
    Solo sumas, restas y omisión:
      +1 -> acumular suma
      -1 -> acumular resta
       0 -> ignorar
    Activaciones: Int16.
    Acumulador: Int32.
    """
    weights = unpack_ternary(packed_weights, num_weights)
    accumulator = 0  # Int32 acumulador
    
    for w, a in zip(weights, activations):
        if w == 1:
            accumulator += a
        elif w == -1:
            accumulator -= a
        # si w == 0, no hace nada (máxima eficiencia energética y computacional)
        
    return accumulator

# ============================================================================
# 3. FUNCIONES DE ACTIVACIÓN ENTERAS (Integer-Only Activations)
# ============================================================================

def relu_int(x: int) -> int:
    """ReLU entera pura."""
    return x if x > 0 else 0

def clamp_int16(x: int) -> int:
    """Clamp a rango Int16 [-32768, 32767]."""
    if x > 32767:
        return 32767
    if x < -32768:
        return -32768
    return x

def integer_softmax_approx(logits: List[int]) -> List[int]:
    """
    Aproximación de Softmax entera en escala fija (0..1000).
    Aproximación lineal/cuadrática por tramos para evitar funciones trascendentes no enteras.
    Suma total exactamente igual a SCALE_BASE (1000).
    """

    if not logits:
        return []
    
    max_logit = max(logits)
    shifted = [relu_int(l - max_logit + 500) for l in logits]
    total = sum(shifted)
    
    if total == 0:
        equal_share = SCALE_BASE // len(logits)
        return [equal_share] * len(logits)
        
    probabilities = [(s * SCALE_BASE) // total for s in shifted]
    # Ajuste de residuo entero
    diff = SCALE_BASE - sum(probabilities)
    probabilities[0] += diff
    return probabilities

# ============================================================================
# 4. MATEMÁTICAS ENTERAS DE PUNTO FIJO (Scaled Integer Math)
# ============================================================================

def integer_accuracy(correct: int, total: int) -> int:
    """Calcula accuracy entero en escala 0 a 1000 (ej. 850 = 85.0%)."""
    if total <= 0:
        return 0
    return (correct * SCALE_BASE) // total

def integer_scale_multiply(val: int, factor_1000: int) -> int:
    """Multiplicación en escala fija entera 1000."""
    return (val * factor_1000) // SCALE_BASE
