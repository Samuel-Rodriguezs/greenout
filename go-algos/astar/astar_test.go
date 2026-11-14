package astar

import "testing"

func TestBuscar(t *testing.T) {
	casos := []struct {
		nome     string
		grade    []string
		ini, fim Ponto
		passos   int // número de células do caminho; 0 = sem caminho
	}{
		{"linha reta", []string{"....."}, Ponto{0, 0}, Ponto{0, 4}, 5},
		{"mesmo ponto", []string{"."}, Ponto{0, 0}, Ponto{0, 0}, 1},
		{"contorna parede", []string{
			"..#..",
			"..#..",
			".....",
		}, Ponto{0, 0}, Ponto{0, 4}, 9},
		{"sem caminho", []string{
			".#.",
			".#.",
		}, Ponto{0, 0}, Ponto{0, 2}, 0},
		{"destino parede", []string{".#"}, Ponto{0, 0}, Ponto{0, 1}, 0},
		{"fora da grade", []string{"."}, Ponto{0, 0}, Ponto{3, 3}, 0},
		{"labirinto", []string{
			".#...",
			".#.#.",
			".#.#.",
			"...#.",
			"##...",
		}, Ponto{0, 0}, Ponto{0, 4}, 11},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			caminho, ok := Buscar(c.grade, c.ini, c.fim)
			if ok != (c.passos > 0) {
				t.Fatalf("ok=%v", ok)
			}
			if !ok {
				return
			}
			if len(caminho) != c.passos {
				t.Errorf("tamanho=%d, esperado %d: %v", len(caminho), c.passos, caminho)
			}
			if caminho[0] != c.ini || caminho[len(caminho)-1] != c.fim {
				t.Errorf("extremos errados: %v", caminho)
			}
			for i := 1; i < len(caminho); i++ {
				if heuristica(caminho[i-1], caminho[i]) != 1 || c.grade[caminho[i].L][caminho[i].C] == '#' {
					t.Errorf("passo inválido %v -> %v", caminho[i-1], caminho[i])
				}
			}
		})
	}
}
