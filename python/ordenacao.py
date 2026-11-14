def bubble_sort(lst):
    a = list(lst)
    for i in range(len(a)):
        trocou = False
        for j in range(len(a) - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                trocou = True
        if not trocou:
            break
    return a


def merge_sort(lst):
    if len(lst) <= 1:
        return list(lst)
    meio = len(lst) // 2
    e, d = merge_sort(lst[:meio]), merge_sort(lst[meio:])
    saida, i, j = [], 0, 0
    while i < len(e) and j < len(d):
        if e[i] <= d[j]:
            saida.append(e[i])
            i += 1
        else:
            saida.append(d[j])
            j += 1
    return saida + e[i:] + d[j:]


def quick_sort(lst):
    if len(lst) <= 1:
        return list(lst)
    p, resto = lst[0], lst[1:]
    return (quick_sort([x for x in resto if x < p]) + [p]
            + quick_sort([x for x in resto if x >= p]))
