// Pacote estaticos serve arquivos de um fs.FS sem listagem de diretórios e com
// Cache-Control configurável.
package estaticos

import (
	"io/fs"
	"net/http"
	"path"
	"strconv"
	"strings"
)

// Handler serve fsys sob o prefixo (ex.: "/static/"). Diretórios só são
// servidos se tiverem index.html; caso contrário respondem 404. maxAge em
// segundos (0 = sem Cache-Control).
func Handler(fsys fs.FS, prefixo string, maxAge int) http.Handler {
	prefixo = "/" + strings.Trim(prefixo, "/")
	if prefixo != "/" {
		prefixo += "/"
	}
	fs_ := http.FileServerFS(fsys)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			w.Header().Set("Allow", "GET, HEAD")
			http.Error(w, "método não permitido", http.StatusMethodNotAllowed)
			return
		}
		rel, ok := strings.CutPrefix(r.URL.Path, prefixo)
		if !ok {
			http.NotFound(w, r)
			return
		}
		nome := path.Clean(rel)
		if nome == "." || nome == "" {
			nome = "."
		}
		if info, err := fs.Stat(fsys, nome); err != nil {
			http.NotFound(w, r)
			return
		} else if info.IsDir() {
			if _, err := fs.Stat(fsys, path.Join(nome, "index.html")); err != nil {
				http.NotFound(w, r)
				return
			}
		}
		if maxAge > 0 {
			w.Header().Set("Cache-Control", "public, max-age="+strconv.Itoa(maxAge))
		}
		r2 := r.Clone(r.Context())
		r2.URL.Path = "/" + rel
		fs_.ServeHTTP(w, r2)
	})
}
