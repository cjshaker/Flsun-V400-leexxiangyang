#!/bin/sh
skip=49

tab='	'
nl='
'
IFS=" $tab$nl"

umask=`umask`
umask 77

gztmpdir=
trap 'res=$?
  test -n "$gztmpdir" && rm -fr "$gztmpdir"
  (exit $res); exit $res
' 0 1 2 3 5 10 13 15

case $TMPDIR in
  / | /*/) ;;
  /*) TMPDIR=$TMPDIR/;;
  *) TMPDIR=/tmp/;;
esac
if type mktemp >/dev/null 2>&1; then
  gztmpdir=`mktemp -d "${TMPDIR}gztmpXXXXXXXXX"`
else
  gztmpdir=${TMPDIR}gztmp$$; mkdir $gztmpdir
fi || { (exit 127); exit 127; }

gztmp=$gztmpdir/$0
case $0 in
-* | */*'
') mkdir -p "$gztmp" && rm -r "$gztmp";;
*/*) gztmp=$gztmpdir/`basename "$0"`;;
esac || { (exit 127); exit 127; }

case `printf 'X\n' | tail -n +1 2>/dev/null` in
X) tail_n=-n;;
*) tail_n=;;
esac
if tail $tail_n +$skip <"$0" | gzip -cd > "$gztmp"; then
  umask $umask
  chmod 700 "$gztmp"
  (sleep 5; rm -fr "$gztmpdir") 2>/dev/null &
  "$gztmp" ${1+"$@"}; res=$?
else
  printf >&2 '%s\n' "Cannot decompress $0"
  (exit 127); res=127
fi; exit $res
�Fάdadxl345.sh �W�n�0}�_��I�*��tR�N�C'MӤ)����BLb��4K�����\�6�%��$����=� ���1򨘀C�-N��|���6����� D��&EG�/f�:��<"����c�N��w�a�!�2N#�-�<@G�g,�}��c��[ëX"ceNM��R��OS��~�|�Ҍǹ<u�#����E�+�AC0�l��4;.�j���e�e�fN}�oj�?c,FS��؏n&d�Cz��Z&u��*8�ܱ�<�W��oɉ{x
MǄן@>a10�?Iֻ�&L �b�r[�C��Cկ��0��U��xX��簇�^�)��.�J$��2��z�\ߛ��^兏�_��1��܌�܎�Mӥ��:=[�[�O���偃ƽ���f1��V>�[�C�(�q��b̘�i�:p�`�`����6�r����v���FIuiEKu���E�'P�k�qUz��!�g<��iĽ���*/X�BYGy�'�М�sW�v?i@$�V�������U�,�dnf�Mi;X1-���K:KT�0h��*���h�3h�|������N�ϳ�%���%�m� ~�d�k���Ї��_�s�'��7�9�7uޱ�=��I�dNڔ9��|%u]�e[����HT{�p��VCY��������:z���\�=1�qX>`���"b�=o������/_G�����������Wf����I��J'5���ՐL���`����n�n^l�s���+6�ϋM���_r���  