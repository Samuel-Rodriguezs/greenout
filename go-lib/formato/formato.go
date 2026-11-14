// Pacote formato converte bytes e durações em texto legível (pt-BR)
// e faz o caminho inverso para tamanhos.
package formato

import (
	"fmt"
	"math"
	"strconv"
	"strings"
	"time"
)

var unidadesIEC = []string{"B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"}

// Bytes formata n usando unidades binárias (1 KiB = 1024 B), com vírgula decimal.
func Bytes(n int64) string {
	if n == 0 {
		return "0 B"
	}
	neg := n < 0
	v := math.Abs(float64(n))
	i := 0
	for v >= 1024 && i < len(unidadesIEC)-1 {
		v /= 1024
		i++
	}
	var s string
	if i == 0 {
		s = fmt.Sprintf("%d %s", int64(v), unidadesIEC[0])
	} else {
		s = strings.Replace(fmt.Sprintf("%.1f %s", v, unidadesIEC[i]), ".", ",", 1)
	}
	if neg {
		return "-" + s
	}
	return s
}

var multiplicadores = map[string]float64{
	"": 1, "b": 1,
	"kb": 1e3, "mb": 1e6, "gb": 1e9, "tb": 1e12, "pb": 1e15,
	"kib": 1 << 10, "mib": 1 << 20, "gib": 1 << 30, "tib": 1 << 40, "pib": 1 << 50,
}

// LerBytes converte textos como "10", "1,5 KiB", "2MB" (SI, 1000) ou "2MiB" (1024) em bytes.
func LerBytes(s string) (int64, error) {
	s = strings.TrimSpace(strings.ToLower(s))
	if s == "" {
		return 0, fmt.Errorf("formato: texto vazio")
	}
	i := 0
	for i < len(s) && (s[i] >= '0' && s[i] <= '9' || s[i] == '.' || s[i] == ',' || (i == 0 && s[i] == '-')) {
		i++
	}
	num := strings.Replace(s[:i], ",", ".", 1)
	un := strings.TrimSpace(s[i:])
	v, err := strconv.ParseFloat(num, 64)
	if err != nil {
		return 0, fmt.Errorf("formato: número inválido em %q", s)
	}
	m, ok := multiplicadores[un]
	if !ok {
		return 0, fmt.Errorf("formato: unidade desconhecida %q", un)
	}
	r := v * m
	if r > math.MaxInt64 || r < math.MinInt64 {
		return 0, fmt.Errorf("formato: valor fora do intervalo: %q", s)
	}
	return int64(math.Round(r)), nil
}

// Duracao formata d de forma compacta: "1d 2h 3min 4s", "250ms", "0s".
// Valores a partir de 1s são truncados em segundos.
func Duracao(d time.Duration) string {
	if d == 0 {
		return "0s"
	}
	prefixo := ""
	if d < 0 {
		prefixo = "-"
		d = -d
		if d < 0 { // math.MinInt64
			d = math.MaxInt64
		}
	}
	switch {
	case d < time.Microsecond:
		return fmt.Sprintf("%s%dns", prefixo, int64(d))
	case d < time.Millisecond:
		return fmt.Sprintf("%s%dµs", prefixo, int64(d/time.Microsecond))
	case d < time.Second:
		return fmt.Sprintf("%s%dms", prefixo, int64(d/time.Millisecond))
	}
	total := int64(d / time.Second)
	dias, total := total/86400, total%86400
	horas, total := total/3600, total%3600
	min, seg := total/60, total%60
	var p []string
	if dias > 0 {
		p = append(p, fmt.Sprintf("%dd", dias))
	}
	if horas > 0 {
		p = append(p, fmt.Sprintf("%dh", horas))
	}
	if min > 0 {
		p = append(p, fmt.Sprintf("%dmin", min))
	}
	if seg > 0 {
		p = append(p, fmt.Sprintf("%ds", seg))
	}
	return prefixo + strings.Join(p, " ")
}
