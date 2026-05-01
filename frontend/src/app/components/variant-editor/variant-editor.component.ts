import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormArray, FormBuilder, Validators, AbstractControl, FormControl } from '@angular/forms';

@Component({
  selector: 'app-variant-editor',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './variant-editor.component.html',
  styleUrls: ['./variant-editor.component.scss']
})
export class VariantEditorComponent implements OnInit {
  @Input() suggestedColors: string[] | null = null;
  @Output() valueChange = new EventEmitter<any>();

  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      product_name: [''],
      brand: [''],
      variants: this.fb.array([])
    });

    this.form.valueChanges.subscribe(v => this.valueChange.emit(v));
  }

  ngOnInit(): void {
    // if suggested colors present, add them as empty variants
    if (this.suggestedColors && this.suggestedColors.length > 0) {
      this.suggestedColors.forEach(c => this.addVariant(c.trim()));
    }
  }

  get variants(): FormArray {
    return this.form.get('variants') as FormArray;
  }

  // Typed accessors to satisfy strict template type checking
  get productNameControl(): FormControl {
    return this.form.get('product_name') as FormControl;
  }

  get brandControl(): FormControl {
    return this.form.get('brand') as FormControl;
  }

  getVariantColorControl(index: number): FormControl {
    return this.variants.at(index).get('color') as FormControl;
  }

  getSizeControl(variantIndex: number, sizeIndex: number): FormControl {
    return (this.variants.at(variantIndex).get('sizes') as FormArray).at(sizeIndex).get('size') as FormControl;
  }

  getStockControl(variantIndex: number, sizeIndex: number): FormControl {
    return (this.variants.at(variantIndex).get('sizes') as FormArray).at(sizeIndex).get('stock') as FormControl;
  }

  newVariant(color = ''): FormGroup {
    return this.fb.group({
      color: [color, [Validators.required]],
      sizes: this.fb.array([])
    });
  }

  addVariant(color = ''): void {
    this.variants.push(this.newVariant(color));
  }

  removeVariant(index: number): void {
    this.variants.removeAt(index);
  }

  sizesOf(variantIndex: number): FormArray {
    return this.variants.at(variantIndex).get('sizes') as FormArray;
  }

  newSize(size: number | null = null, stock: number | null = null): FormGroup {
    return this.fb.group({
      size: [size, [Validators.required, Validators.min(0), Validators.max(50)]],
      stock: [stock ?? 0, [Validators.required, Validators.min(0)]]
    }, { validators: this.noDuplicateSizeValidator() });
  }

  addSize(variantIndex: number, size: number | null = null, stock: number | null = null): void {
    const sizes = this.sizesOf(variantIndex);
    sizes.push(this.newSize(size, stock));
  }

  removeSize(variantIndex: number, sizeIndex: number): void {
    const sizes = this.sizesOf(variantIndex);
    sizes.removeAt(sizeIndex);
  }

  // Prevent duplicate sizes within the same variant
  noDuplicateSizeValidator() {
    return (group: AbstractControl) => {
      const parent = group.parent as FormArray | null;
      if (!parent) return null;
      // collect sizes
      const sizes = parent.controls.map((c: any) => c.get('size')?.value).filter((s: any) => s !== null && s !== undefined);
      const last = group.get('size')?.value;
      const occurrences = sizes.filter((s: any) => s === last).length;
      return occurrences > 1 ? { duplicateSize: true } : null;
    };
  }

  // helper to get total stock
  totalStock(): number {
    let total = 0;
    this.variants.controls.forEach(v => {
      const sizes = (v.get('sizes') as FormArray).controls;
      sizes.forEach(s => {
        const stock = Number(s.get('stock')?.value) || 0;
        total += stock;
      });
    });
    return total;
  }

  availabilityLabel(): string {
    const total = this.totalStock();
    if (total > 10) return 'Alta disponibilidad';
    if (total < 5) return 'Stock bajo';
    return 'Stock moderado';
  }

  // Prefill colors (can be called by parent)
  prefillColors(colors: string[]): void {
    if (!colors || colors.length === 0) return;
    // clear existing
    while (this.variants.length) {
      this.variants.removeAt(0);
    }
    colors.forEach(c => this.addVariant(c));
  }

  // produce JSON structure as requested
  getValue(): any {
    return {
      product_name: this.form.get('product_name')?.value || '',
      brand: this.form.get('brand')?.value || '',
      variants: this.variants.controls.map(v => ({
        color: v.get('color')?.value,
        sizes: (v.get('sizes') as FormArray).controls.map(s => ({ size: Number(s.get('size')?.value), stock: Number(s.get('stock')?.value) }))
      }))
    };
  }
}
