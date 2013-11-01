Blender-Smoothgroups
====================

A way to edit vertex normals. Usefull for low poly modelling.

http://vimeo.com/78378752

It creates a panel called Smooth Groups in the object data of meshes. Click the + icon to add a smoothgroup, assign some faces to it, then press Smooth.
The smoothing is lost when entering edit mode or changing editing the mesh. Face selection is stored thow, so simply press Smooth again.
Feels a bit hacky because the script stores data in the custom properties of the mesh. If you don't edit these properties everything should work fine.

Unfortunatly this is incompatible with the edge split modifyer since the edge split will smooth the vertex normals again after the script has set them.
Workaround is to apply the edge split modifyer, but that's destructive :-(

http://blenderartists.org/forum/showthread.php?283027-editing-vertex-normals-(smoothgroups)-script-in-the-works
