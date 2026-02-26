using UnityEngine;
using UnityEditor;

/// <summary>
/// Editor menu to create the Architect pose bridge (PoseReceiver + PoseAvatarDriver) in the scene.
/// </summary>
public static class ArchitectSetup
{
    [MenuItem("Architect/Create Pose Bridge")]
    public static void CreatePoseBridge()
    {
        var go = new GameObject("PoseBridge");
        go.AddComponent<PoseReceiver>();
        var driver = go.AddComponent<PoseAvatarDriver>();
        driver.createDebugSkeleton = true;
        driver.createLimbSticks = true;
        driver.mirrorFlipX = true;
        driver.avatarScale = 2f;
        Undo.RegisterCreatedObjectUndo(go, "Create Pose Bridge");
        Selection.activeGameObject = go;
        Debug.Log("[Architect] PoseBridge created. Start pose_webcam.py with --udp-port 5555 and enter Play mode.");
    }
}
