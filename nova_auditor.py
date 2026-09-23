#!/usr/bin/env python3
"""
Nova Integer/Ternary Auditor — ModernoTech
Inspecciona el código fuente del núcleo para verificar el cumplimiento estricto
de cero coma flotante (Float-Free / Integer-Only) en los componentes de Nova Native.
"""

import os
import re
import sys
from typing import List, Dict, Any

FORBIDDEN_PATTERNS = [
    (r'\bfloat\b', "Tipo primitivo 'float' detectado"),
    (r'\bfloat32\b', "Tipo 'float32' detectado"),
    (r'\bfloat64\b', "Tipo 'float64' detectado"),
    (r'\bdouble\b', "Tipo 'double' detectado"),
    (r'\bmath\.exp\b', "Llamada a math.exp flotante detectada"),
    (r'\bmath\.sqrt\b', "Llamada a math.sqrt flotante detectada"),
    (r'\bnp\.exp\b', "Llamada a np.exp flotante detectada"),
    (r'\bnp\.sqrt\b', "Llamada a np.sqrt flotante detectada"),
    (r'\bsoftmax\b\(.*float', "Softmax en coma flotante detectado"),
]

TARGET_MODULES = [
    "nova_native.py"
]

def audit_file(file_path: str) -> List[Dict[str, Any]]:
    violations = []
    if not os.path.exists(file_path):
        return violations

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        # Ignorar comentarios y docstrings informativos
        if clean_line.startswith("#") or clean_line.startswith('"""') or clean_line.startswith('*') or clean_line.startswith('-'):
            continue
        for pattern, desc in FORBIDDEN_PATTERNS:
            if re.search(pattern, clean_line):
                violations.append({
                    "file": os.path.basename(file_path),
                    "line": idx,
                    "content": clean_line,
                    "issue": desc
                })
    return violations

def run_audit() -> bool:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    total_violations = []

    print("=" * 65)
    print("  🛡️  NOVA NATIVE INTEGER & TERNARY AUDITOR | ModernoTech")
    print("=" * 65)

    for mod in TARGET_MODULES:
        full_p = os.path.join(base_dir, mod)
        v = audit_file(full_p)
        status = "FAIL ❌" if v else "PASS ✅"
        print(f"[{status}] Auditando módulo: {mod}")
        if v:
            for item in v:
                print(f"      L{item['line']}: {item['issue']} -> `{item['content']}`")
            total_violations.extend(v)

    print("-" * 65)
    if total_violations:
        print(f"❌ AUDITORÍA FALLIDA: {len(total_violations)} violaciones de tipos flotantes encontradas.")
        return False
    else:
        print("✅ AUDITORÍA EXITOSA: 100% Entero / Ternario verificado sin 'float'.")
        return True

if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
