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
����cusb.sh ��n�@���SL�H��̲�D�R�/ЛJ��"��Vcy�4���]��`;2I���2�ygg��ݿ jˀږ�}�W7�ώ?*�"eHGh}'�G��lF2�E4WF`-�����E	����r!h(�ܗa(���<9�yބ����M��l��jo�ᇜ���<}��jkR�$�7�TU4O
�PW<R%"i��^�ҥ��/L#�� �؈�$k�_by�3J���T�}���*����)�U�;3�0��ό�ۉ��r"ƪ����L��@��^�dxM	D�_٢���:����x��#�y�U<�-i3 _c���L��kl/B��n�3}��w� �9�r���@)��g�,;+�.H�o��- �}��U�b�{�2�W�`1?��MT5R�LrA��	��;}�T��9�N���
�H�'픢�\�G�ȓM�P����4*Z9�ke�����f��f+g�r��%d� k��fުf�Aͼ����M�����2�>Z�+<���&�l�&�P�2#M(qp�kzk�nM �ӷ%��Y�W[/�#�XѢ�tք>(;�:韾�J2��!���<{d���n9i��>���B�G_�x�*N��o�����=����w#��ok�.�N��e�x^sķ5Ǯ���(^k�ь�e��fj�� �w���v������ioi��xCq;�E��Z$[���u����삟�.��]�a��]���&��  