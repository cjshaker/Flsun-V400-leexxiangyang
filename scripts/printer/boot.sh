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
����dboot.sh �Wmo�6�\��@�0�"�lF�HZ�+��ż����d�,K�ȼ8���(R��ڲ�$Pﹷ����	��{.�=���+n9P�R<��mܽe�4��	'A���p+si��u������ri��F�O� �B�d�a �@? <K�!�Ga��l�Oau�����3 ̟%��p3u0$�����7��Ø/K�/�Tm~A�S�X�B��r�f��T��)��J�-9�3�b��,L/Ű�U���u>A߄�M$��c����8���f�xS@*�l�L����ڬ�3>�Y�z�0��E�=]�ktHDeF�~8)*�R&[t"��"�ͣ�a�^�vr�� �ٚ��?�H�F���e�W&��y<o^*z,ݍ���l��6Q�W����Eq:����8�Rt�-.��"����ަDIp�?��>��+�5��g��}&<��s��ۛ����Y�<�Kw�nq�ɡQ���j��Zyo&@ه�^$I��s)��q�uml���6���BϞ 8���V]��.�s5Ȼe�&������>�&�<E���m�9�?z�=u����Ёi�"YB[,
��ߐ녞
�ܡg�ۍ+A�A�e��ڰ�v��6m�s�8����rH�2�%��!�������R��@�-:�'�1��Ŵk��HN*%z���8�st��9ބJ�~���dTf�����19�:���oXjԼ���i&Q�v������q�?��%�޲��b&������c�Br�ͷf`����{#��ݲ�(�i T���ʆ2'kyUG�����݈`�8�TV�o�KTǀ�������I��{26��m� �_�	�^��IQ��9���<b2��T����9�����ˆ�6�}f�[b����W�7�߆��ǯ/}�����Bn5��PE�jI;�������������5u�`K�8ɘ"w��;O�<mX��	|e�}��ji?�Z����_l`�  