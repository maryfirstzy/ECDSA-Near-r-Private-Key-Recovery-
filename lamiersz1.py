# -*- coding: utf-8 -*-
# recover_near_r.py
# Zakłada: r1,r2,s1,s2,z1,z2,n są liczbami całkowitymi (int)
# Działa gdy k2 = k1 + t dla niewielkiego całkowitego t (np. |t| <= 2^20 zależnie od zasobów).

def mod_inv(a: int, n: int) -> int:
    """Odwrotność a modulo n. Rzuca ValueError jeśli brak odwrotności."""
    a = a % n
    try:
        return pow(a, -1, n)
    except ValueError:
        raise ValueError(f"Brak odwrotności modulo n dla a = {a} (mod {n}).")

def try_recover_near_r(r1: int, r2: int, s1: int, s2: int, z1: int, z2: int,
                       n: int, max_delta: int = 2**20, verbose: bool = False):
    """
    Próbuj odzyskać k1, k2 i d gdy k2 = k1 + t i |t| <= max_delta.
    Zwraca listę wszystkich znalezionych rozwiązań w postaci krotek (k1, k2, d, t).
    Uwaga: koszt liniowy w liczbie testowanych t.
    """
    r1 = int(r1) % n
    r2 = int(r2) % n
    s1 = int(s1) % n
    s2 = int(s2) % n
    z1 = int(z1) % n
    z2 = int(z2) % n

    results = []

    coeff = (r2 * s1 - r1 * s2) % n  # współczynnik przy k1
    if coeff == 0:
        # Współczynnik zerowy oznacza specjalny przypadek — nie da się rozwiązać liniowo.
        # Można wtedy spróbować inne podejścia, ale tutaj zgłaszamy błąd.
        raise ValueError("Współczynnik (r2*s1 - r1*s2) ≡ 0 (mod n) — liniowe rozwiązanie niemożliwe.")

    inv_coeff = None
    try:
        inv_coeff = mod_inv(coeff, n)
    except ValueError:
        raise ValueError("Brak odwrotności współczynnika (r2*s1 - r1*s2) mod n — nie można rozwiązać.")

    # przeszukujemy t w [-max_delta, max_delta]
    # Zalecenie: zacznij od małego max_delta (np. 1000) i zwiększ jeśli chcesz.
    for t in range(-max_delta, max_delta + 1):
        # prawa strona równania
        rhs = (r2 * z1 - r1 * z2 + (r1 * s2 * (t % n))) % n
        # oblicz k1
        k1 = (rhs * inv_coeff) % n
        k2 = (k1 + t) % n

        # oblicz d z pierwszego równania: r1 * d ≡ s1*k1 - z1  (mod n)
        if r1 % n == 0:
            # r1 ≡ 0 (mod n) niespotykane w secp256k1, ale sprawdzamy
            continue
        try:
            inv_r1 = mod_inv(r1, n)
        except ValueError:
            continue
        d_candidate = ((s1 * k1 - z1) % n) * inv_r1 % n

        # weryfikacja: sprawdź, czy druga równoważność też się zgadza:
        # s2 ≡ k2^{-1} * (z2 + r2*d)  (mod n)
        # => left = s2, right = (z2 + r2*d) * k2^{-1} mod n
        # musimy mieć odwrotność k2
        if k2 % n == 0:
            continue
        try:
            inv_k2 = mod_inv(k2, n)
        except ValueError:
            continue

        right = ((z2 + r2 * d_candidate) % n) * inv_k2 % n
        if right == s2:
            # rozwiązanie zaakceptowane
            results.append((k1, k2, d_candidate, t))
            if verbose:
                print(f"Znaleziono: t={t}, k1={hex(k1)}, k2={hex(k2)}, d={hex(d_candidate)}")
            # jeśli chcesz przerwać po pierwszym wyniku, odkomentuj nast. linię:
            # break

    return results

# -------------------------
# Przykład użycia:
if __name__ == "__main__":
    # Wstaw swoje wartości (możesz użyć int('hexstring', 16) jeśli masz hex)
    r1 = 0xced8474e7cbb2c9ade8b4a6474c3fa8ea4036718d844f3105dde155a6583a134   # zamień
    r2 = 0xe6ab0f2d4d4f90f336876ced966ff265b0e050f8585abefd14a75056f816d494
    s1 = 0x1c9e070de661d5913d457c6f075641ec28c8c8f4fe336070710787e471ebd558
    s2 = 0x81c29f749fcec4c35497798b3e2ceeab0ee268279a5f70e847fcb6062c830e13
    z1 = 0x0cf7190cc6c1f95b987e0e284e4eba44552f89662272b850b059a8dc0d8905a8
    z2 = 0x66c0f25668799a35931bc4746a97d032796af0ba4e898f6691ea063f78f59036

    # rząd krzywej secp256k1:
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    # spróbuj z małym przeszukaniem, np. max_delta = 2**16 (65536) -> koszt 131k iteracji (oba kierunki)
    solutions = try_recover_near_r(r1, r2, s1, s2, z1, z2, n, max_delta=2**16, verbose=True)

    print(f"Znaleziono {len(solutions)} rozwiązań.")
    for k1, k2, d, t in solutions:
        print("t =", t)
        print("k1 =", hex(k1))
        print("k2 =", hex(k2))
        print("d  =", hex(d))
        print("----")
