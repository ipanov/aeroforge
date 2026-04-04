"""
Rudder 3MF Export — Generate print-ready 3MF from STL mesh.
=============================================================
Run: cd D:/Repos/aeroforge && PYTHONPATH=. python scripts/build_rudder_3mf.py
"""
import sys
import os
import numpy as np
import trimesh
import lib3mf

STL_PATH = "cad/components/empennage/Rudder/Rudder.stl"
OUT_PATH = "cad/components/empennage/Rudder/Rudder.3mf"


def make_3mf(mesh, path, name, r, g, b, a=140):
    """Export a trimesh mesh to 3MF format with color."""
    wrapper = lib3mf.get_wrapper()
    model = wrapper.CreateModel()
    model.SetUnit(lib3mf.ModelUnit.MilliMeter)

    mo = model.AddMeshObject()
    mo.SetName(name)

    for v in mesh.vertices:
        p = lib3mf.Position()
        p.Coordinates[0] = float(v[0])
        p.Coordinates[1] = float(v[1])
        p.Coordinates[2] = float(v[2])
        mo.AddVertex(p)

    for f in mesh.faces:
        if f[0] == f[1] or f[1] == f[2] or f[0] == f[2]:
            continue
        t = lib3mf.Triangle()
        t.Indices[0] = int(f[0])
        t.Indices[1] = int(f[1])
        t.Indices[2] = int(f[2])
        mo.AddTriangle(t)

    # Add color
    cg = model.AddColorGroup()
    c = lib3mf.Color()
    c.Red = r
    c.Green = g
    c.Blue = b
    c.Alpha = a
    pid = cg.AddColor(c)

    # Apply color to all triangles
    rid = cg.GetResourceID()
    for i in range(mo.GetTriangleCount()):
        props = lib3mf.TriangleProperties()
        props.ResourceID = rid
        props.PropertyIDs[0] = pid
        props.PropertyIDs[1] = pid
        props.PropertyIDs[2] = pid
        mo.SetTriangleProperties(i, props)

    mo.SetObjectLevelProperty(rid, pid)
    model.AddBuildItem(mo, wrapper.GetIdentityTransform())

    writer = model.QueryWriter("3mf")
    writer.WriteToFile(path)
    print(f"  3MF exported: {path}")


def main():
    print("Exporting Rudder 3MF...")
    mesh = trimesh.load(STL_PATH)
    print(f"  Loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # Purple color matching the project color scheme (white/purple/pink)
    make_3mf(mesh, OUT_PATH, "Rudder", r=139, g=92, b=246, a=255)

    # Verify
    file_size = os.path.getsize(OUT_PATH)
    print(f"  File size: {file_size / 1024:.1f} KB")
    print("Rudder 3MF export complete.")


if __name__ == "__main__":
    main()
