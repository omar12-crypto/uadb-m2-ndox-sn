#!/usr/bin/env python3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


ZONES = ['DAKAR_NORD', 'DAKAR_SUD', 'PIKINE', 'THIES',
         'SAINT_LOUIS', 'KAOLACK', 'ZIGUINCHOR']

COORDS = {
    'DAKAR_NORD':    (14.73, -17.45),
    'DAKAR_SUD':     (14.67, -17.43),
    'PIKINE':        (14.75, -17.38),
    'THIES':         (14.79, -16.93),
    'SAINT_LOUIS':   (16.03, -16.50),
    'KAOLACK':       (14.15, -16.08),
    'ZIGUINCHOR':    (12.55, -16.27),
}


def generer_donnees_test():
    np.random.seed(42)
    scores = {}
    for zone in ZONES:
        score = round(np.random.uniform(0.1, 0.9), 3)
        scores[zone] = score
    return scores


def tracer_barplot_priorites(scores, output_path='dashboard/dashboard_priorites.png'):
    zones = sorted(scores, key=scores.get, reverse=True)
    valeurs = [scores[z] for z in zones]

    plt.figure(figsize=(10, 6))
    colors = ['#e74c3c' if v < 0.3 else '#f39c12' if v < 0.6 else '#3498db' if v < 0.8 else '#2ecc71'
              for v in valeurs]
    bars = plt.barh(zones, valeurs, color=colors, edgecolor='grey')
    plt.xlabel('Score de priorité')
    plt.title('Priorités de maintenance par zone — Ndocx-SN')
    for bar, v in zip(bars, valeurs):
        plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                 f'{v:.3f}', va='center')

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"✓ Dashboard sauvegardé : {output_path}")
    plt.close()


def optimiser_tournees(scores, depot='DAKAR_NORD'):
    zones_triees = sorted(scores, key=scores.get)
    trois_prioritaires = zones_triees[:3]

    depot_coord = np.array(COORDS[depot])
    visitees = [depot]
    restantes = list(trois_prioritaires)

    while restantes:
        derniere = COORDS[visitees[-1]]
        distances = [np.linalg.norm(np.array(COORDS[z]) - np.array(derniere)) for z in restantes]
        prochaine = restantes[np.argmin(distances)]
        visitees.append(prochaine)
        restantes.remove(prochaine)

    return visitees


def main():
    print("=== Ndocx-SN : Tableau de bord des priorités ===")

    scores = generer_donnees_test()

    print("\nScores de priorité par zone :")
    for zone, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {zone}: {score:.3f}")

    tracer_barplot_priorites(scores)

    print("\nOptimisation des tournées (plus proche voisin) :")
    tournees = optimiser_tournees(scores)
    print("  Itinéraire : " + " → ".join(tournees))

    print("\n✓ Dashboard généré avec succès.")


if __name__ == '__main__':
    main()