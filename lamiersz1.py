# -*- coding: utf-8 -*-
# recover_near_r.py
# Zakłada: r1,r2,s1,s2,z1,z2,n są liczbami całkowitymi (int)
# Działa gdy k2 = k1 + t dla niewielkiego całkowitego t (np. |t| <= 2^256 zależnie od zasobów).

def mod_inv(a: int, n: int) -> int:
    """Odwrotność a modulo n. Rzuca ValueError jeśli brak odwrotności."""
    a = a % n
    try:
        return pow(a, -1, n)
    except ValueError:
        raise ValueError(f"Brak odwrotności modulo n dla a = {a} (mod {n}).")

def try_recover_near_r(r1: int, r2: int, s1: int, s2: int, z1: int, z2: int,
                       n: int, max_delta: int = 2**256, verbose: bool = False):
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
    r1 = 0xbaf2aa695873ee637a1b23b53a78c512e4ea8ed72738badbdac3fe6b2a769176       # zamień
    r2 = 0xd56a07721d620e6b3c64021713ae2cec9bc831c4d6d32501e347142bff70d078
    s1 = 0xb47bbe4d2e405452dfa95bbd6ac3804c38c25f838edafd5ceb3456f3b040b0a6
    s2 = 0x4c136bac45a92b2adfc0af27282b494f6dc416535433d36e04057de2bf7cc326
    z1 = 0xd20aff079cd86074eff889e1f4f0fbd0b97ef4eeff378147afc815d8a28552d5
    z2 = 0x17ea532a30334538c281467befb5fca7e66c6b1e760f5d17d77cb853c65a3c7d 

    # rząd krzywej secp256k1:
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

    # spróbuj z małym przeszukaniem, np. max_delta = 2**256 (115792089237316195423570985008687907852837564279074904382605163141518161494337) -> koszt 131k iteracji (oba kierunki)
    solutions = try_recover_near_r(r1, r2, s1, s2, z1, z2, n, max_delta=2**256, verbose=True)

    print(f"Znaleziono {len(solutions)} rozwiązań.")
    for k1, k2, d, t in solutions:
        print("t =", t)
        print("k1 =", hex(k1))
        print("k2 =", hex(k2))
        print("d  =", hex(d))
        print("----")
