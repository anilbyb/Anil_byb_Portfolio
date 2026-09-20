(defun c:ExportLayersToCSV ()
  (setq filename (getfiled "Select Output File" "" "csv" 1))
  (if filename
    (progn
      (setq file (open filename "w"))
      (setq layerTable (vla-get-layers (vla-get-activedocument (vlax-get-acad-object))))
      (write-line "LayerName, Linetype" file)
      (vlax-for layer layerTable
        (setq layerName (vla-get-name layer))
        (setq layerLinetype (vla-get-linetype layer))
        (write-line (strcat layerName ", " layerLinetype) file)
      )
      (close file)
      (princ (strcat "\nLayer information exported to " filename))
    )
    (princ "\nExport cancelled.")
  )
  (princ)
)

(princ "\nType 'ExportLayersToCSV' to export layers and linetypes to a CSV file.\n")
(princ)
